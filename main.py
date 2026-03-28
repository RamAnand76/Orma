
import os
import sys
import asyncio
import time
import logging
import threading
import queue
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from orma_core import OrmaEngine
from orma_voice import OrmaVoice
import config

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("orma.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ORMA_MAIN")

# Load configuration from .env
load_dotenv()

# --- GEMINI / OPENROUTER SETUP ---
gemini_key = os.environ.get("GEMINI_API_KEY")
openrouter_key = os.environ.get("OPENROUTER_API_KEY")

if gemini_key:
    genai.configure(api_key=gemini_key)

# Global rotation state
ENABLE_MODEL_ROTATION = os.environ.get("ENABLE_MODEL_ROTATION", "False").lower() == "true"
ROTATION_MODELS = [m.strip() for m in os.environ.get("ROTATION_MODELS", "google/gemma-3-27b-it:free").split(',')] if ENABLE_MODEL_ROTATION else ['gemma-3-27b-it']
rotation_index = 0

def llm_caller(system_prompt, user_prompt):
    """Wrapper to handle LLM API calls with circular model switching."""
    global rotation_index
    
    combined_prompt = f"{system_prompt}\n\nUser Input: {user_prompt}"
    max_attempts = len(ROTATION_MODELS)
    
    for attempt in range(max_attempts):
        current_model = ROTATION_MODELS[rotation_index % len(ROTATION_MODELS)]
        logger.info(f"Using model: {current_model}")
        
        try:
            result_text = ""
            if "/" in current_model or openrouter_key:
                if not openrouter_key:
                    logger.error("Error: OPENROUTER_API_KEY missing.")
                    return ""
                    
                headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
                data = {
                    "model": current_model,
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    "temperature": config.GENERATION_TEMPERATURE
                }
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                if response.status_code == 200:
                    result_text = response.json()['choices'][0]['message']['content']
                else:
                    logger.error(f"OpenRouter Error {response.status_code}")
                    result_text = ""
            else:
                if not gemini_key: return ""
                model = genai.GenerativeModel(current_model)
                response = model.generate_content(combined_prompt, generation_config={"temperature": config.GENERATION_TEMPERATURE})
                result_text = response.text
                
            if result_text:
                if ENABLE_MODEL_ROTATION: rotation_index += 1
                return result_text
            else:
                if ENABLE_MODEL_ROTATION: rotation_index += 1
                
        except Exception as e:
            logger.error(f"LLM Error on {current_model}: {e}")
            if ENABLE_MODEL_ROTATION: rotation_index += 1

    return ""

# --- SHARED STATE ---
input_queue = queue.Queue()
running = True
last_interaction_time = time.time()
last_evolution_time = time.time()

def input_listener():
    """Thread: Listens for user input."""
    global running
    while running:
        try:
            user_in = input() 
            input_queue.put(user_in)
        except EOFError:
            running = False
            break

async def main_loop():
    global running, last_interaction_time, last_evolution_time
    
    logger.info("Orma V7 (Evolution & Voice) Initializing...")
    engine = OrmaEngine(llm_caller)
    
    # Initialize Voice
    voice = None
    if config.ENABLE_VOICE:
        voice = OrmaVoice(voice=config.VOICE_NAME, rate=config.VOICE_RATE, volume=config.VOICE_VOLUME)
        logger.info(f"Voice Enabled: {config.VOICE_NAME}")

    # Start Input Thread
    threading.Thread(target=input_listener, daemon=True).start()

    # Diagnostics
    print("-" * 40)
    print(f"📂 Memory Nodes : {engine.ltm.graph.number_of_nodes()}")
    print(f"❤️  Trust Level  : {engine.psyche.state['stats']['trust']}/100")
    print(f"🎯 Current Goal : {engine.psyche.state['internal'].get('short_term_goal', 'None')}")
    print("-" * 40)
    print("\n✅ System Ready. Say 'exit' to quit.\n")
    print("You: ", end="", flush=True)

    while running:
        # 1. Process User Input
        try:
            user_in = input_queue.get_nowait()
            
            if user_in.lower() in ["exit", "quit"]: 
                print("\n🛑 Shutting down...")
                engine.consolidate_memory() 
                engine.psyche.save() 
                running = False
                break
            
            if user_in.strip():
                response = engine.process(user_in)
                print(f"\n🤖 Orma: {response}\n")
                
                # Speak if enabled
                if voice:
                    await voice.speak(response)
                
                last_interaction_time = time.time()
                last_evolution_time = time.time() # Delay evolution after chat
                print("You: ", end="", flush=True)
                
        except queue.Empty:
            # 2. Background Evolution Logic
            idle_time = time.time() - last_interaction_time
            time_since_evolve = time.time() - last_evolution_time
            
            if config.ENABLE_BACKGROUND_RESEARCH and idle_time > config.EVOLUTION_INTERVAL:
                if time_since_evolve > config.EVOLUTION_INTERVAL:
                    # Trigger Evolution
                    engine.evolve()
                    last_evolution_time = time.time()
                    # After evolving, we don't reprompt "You:" to avoid cluttering idle screen
            
            await asyncio.sleep(0.1)

    logger.info("Shutting down Orma.")

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass