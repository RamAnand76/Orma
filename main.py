import os
import sys
import time
import logging
import threading
import queue
import google.generativeai as genai
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

# Replace with your actual key or ensure it's in your environment variables
os.environ["GEMINI_API_KEY"] = "AIzaSyCx_FS0a0qR-umuI9Ge4lDMx0aqXq89nu8" 

# --- GEMINI SETUP ---
if "GEMINI_API_KEY" not in os.environ:
    logger.error("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemma-3-27b-it') # Using the requested model

def gemini_caller(system_prompt, user_prompt):
    """Wrapper to handle Gemini API calls."""
    combined_prompt = f"{system_prompt}\n\nUser Input: {user_prompt}"
    try:
        response = model.generate_content(
            combined_prompt,
            generation_config={"temperature": config.GENERATION_TEMPERATURE}
        )
        return response.text
    except Exception as e:
        logger.error(f"GEMINI ERROR: {e}") 
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
    engine = OrmaEngine(gemini_caller)
    
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