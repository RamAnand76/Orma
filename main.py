import google.generativeai as genai
import os
import sys
import logging
from orma_core import OrmaEngine

# --- 0. LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("orma.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- 1. SETUP GEMINI ---
# Replace with your actual key or ensure it's in your environment variables
os.environ["GEMINI_API_KEY"] = "AIzaSyCx_FS0a0qR-umuI9Ge4lDMx0aqXq89nu8" 

if not os.environ.get("GEMINI_API_KEY") or "API_KEY_HERE" in os.environ["GEMINI_API_KEY"]:
    logger.error("Please set your Gemini API Key in line 23 of main.py")
    sys.exit()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemma-3-27b-it')

def gemini_caller(system_prompt, user_prompt):
    """Wrapper to handle Gemini API calls."""
    combined_prompt = f"{system_prompt}\n\nUser Input: {user_prompt}"
    try:
        response = model.generate_content(combined_prompt)
        return response.text
    except Exception as e:
        logger.error(f"GEMINI ERROR: {e}") 
        return ""

# --- 2. START ORMA ---
# --- 2. START ORMA ---
if __name__ == "__main__":
    logger.info("Orma V5 (Soul Edition) Initializing...")
    
    # Initialize Engine
    engine = OrmaEngine(llm_function=gemini_caller)
    
    # --- DIAGNOSTICS DASHBOARD ---
    # We grab stats from the new Psyche module to show you the "Soul" state
    node_count = engine.ltm.graph.number_of_nodes()
    soul_stats = engine.psyche.state['stats']
    current_obsession = engine.psyche.state['internal']['current_obsession']
    
    print("-" * 40)
    print(f"📂 Memory Nodes : {node_count}")
    print(f"❤️  Trust Level  : {soul_stats['trust']}/100")
    print(f"⚡ Energy Level : {soul_stats['energy']}/100")
    print(f"🎭 Current Mood : {soul_stats['mood']}")
    print(f"🧐 Obsession    : {current_obsession}")
    print("-" * 40)
    
    logger.info("System Ready.")
    print("\n✅ System Ready. Say 'exit' to quit.")
    
    # --- 3. THE MAIN LOOP (This was missing!) ---
    while True:
        try:
            user_in = input("\nYou: ")
            if user_in.lower() in ["exit", "quit"]: 
                engine.psyche.save() # Save soul state before leaving
                break
            
            # Process the input through Orma Engine
            engine.process(user_in)
            
        except KeyboardInterrupt:
            print("\nForce stopping...")
            break
        except Exception as e:
            logger.error(f"Runtime Error: {e}")
            break
            
    logger.info("Shutting down.")