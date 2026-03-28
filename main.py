import os
import sys
import time
import logging
import threading
import queue
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from orma_core import OrmaEngine
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
        logger.info(f"Using model: {current_model} (Rotation Index: {rotation_index})")
        
        try:
            result_text = ""
            # OPENROUTER LOGIC
            if "/" in current_model or openrouter_key:
                if not openrouter_key:
                    logger.error("Error: OPENROUTER_API_KEY environment variable not set.")
                    return ""
                    
                headers = {
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": current_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": config.GENERATION_TEMPERATURE
                }
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                
                if response.status_code == 200:
                    result_text = response.json()['choices'][0]['message']['content']
                else:
                    logger.error(f"OpenRouter API Error {response.status_code}: {response.text}")
                    result_text = ""
                    
            # FALLBACK GEMINI NATIVE LOGIC
            else:
                if not gemini_key:
                    logger.error("Error: GEMINI_API_KEY environment variable not set.")
                    return ""
                model = genai.GenerativeModel(current_model)
                response = model.generate_content(
                    combined_prompt,
                    generation_config={"temperature": config.GENERATION_TEMPERATURE}
                )
                result_text = response.text
                
            # If successful, increment for next time and return
            if result_text:
                if ENABLE_MODEL_ROTATION:
                    rotation_index += 1
                return result_text
            else:
                logger.warning(f"Model {current_model} failed (empty/error). Auto-falling back to next model...")
                if ENABLE_MODEL_ROTATION:
                    rotation_index += 1
                
        except Exception as e:
            logger.error(f"LLM CALL ERROR on {current_model}: {e}") 
            if ENABLE_MODEL_ROTATION:
                rotation_index += 1

    logger.error("All models in the rotation failed. Rate limits might be exhausted.")
    return ""

# --- SHARED STATE ---
input_queue = queue.Queue()
running = True
last_interaction_time = time.time()

def input_listener():
    """Thread 1: Listens for user input without blocking the main loop."""
    global running
    while running:
        try:
            # This is still blocking, but in a thread, so it doesn't freeze the brain
            user_in = input() 
            input_queue.put(user_in)
        except EOFError:
            running = False
            break

# --- MAIN LOOP ---
def main():
    global running, last_interaction_time
    
    logger.info("Orma V6 (Autonomous Edition) Initializing...")
    engine = OrmaEngine(llm_caller)
    
    # 1. Start Input Thread
    listener = threading.Thread(target=input_listener, daemon=True)
    listener.start()

    # --- DIAGNOSTICS DASHBOARD ---
    node_count = engine.ltm.graph.number_of_nodes()
    soul_stats = engine.psyche.state['stats']
    current_goal = engine.psyche.state['internal'].get('current_goal', 'None')
    
    print("-" * 40)
    print(f"📂 Memory Nodes : {node_count}")
    print(f"❤️  Trust Level  : {soul_stats['trust']}/100")
    print(f"⚡ Energy Level : {soul_stats['energy']}/100")
    print(f"🎭 Current Mood : {soul_stats['mood']}")
    print(f"🎯 Current Goal : {current_goal}")
    print("-" * 40)
    
    logger.info("System Ready. Spontaneous Mode: OFF (Event-Driven).")
    print("\n✅ System Ready. Say 'exit' to quit. (I might speak first...)\n")
    print("You: ", end="", flush=True) # Initial prompt

    while running:
        # A. Check for User Input (Non-blocking check)
        try:
            user_in = input_queue.get_nowait() # Non-blocking get
            
            # --- PROCESS USER INPUT ---
            if user_in.lower() in ["exit", "quit"]: 
                print("\n🛑 Shutting down...")
                engine.consolidate_memory() 
                engine.psyche.save() 
                running = False
                break
            
            if user_in.strip():
                # Process normally
                response = engine.process(user_in)
                print(f"\n🤖 Orma: {response}\n")
                last_interaction_time = time.time() # Reset bored timer
                print("You: ", end="", flush=True) # Reprompt
            
        except queue.Empty:
            # B. User is Silent -> Just wait (Event Driven)
            time.sleep(0.1) 
            # Spontaneous Mode DISABLED per user request (Too robotic/philosophical)

    logger.info("Shutting down.")

if __name__ == "__main__":
    main()