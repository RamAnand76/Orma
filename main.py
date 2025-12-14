import google.generativeai as genai
import os
from orma_core import OrmaEngine

# --- 1. SETUP GEMINI ---
# Get your key from: https://aistudio.google.com/app/apikey
os.environ["GEMINI_API_KEY"] = "AIzaSyCx_FS0a0qR-umuI9Ge4lDMx0aqXq89nu8"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# ✅ FIX 1: Use a valid API model name
# 'gemini-1.5-flash' is the best for speed/memory. 
model = genai.GenerativeModel('gemma-3-27b-it')

def gemini_caller(system_prompt, user_prompt):
    """
    The wrapper that Orma uses to talk to Gemini.
    """
    # We combine them because some Gemini versions are strict about system prompts
    combined_prompt = f"{system_prompt}\n\nUser Input: {user_prompt}"
    try:
        response = model.generate_content(combined_prompt)
        return response.text
    except Exception as e:
        # ✅ FIX 2: Print errors so we know if it fails
        print(f"\n❌ GEMINI ERROR: {e}") 
        return ""

# --- 2. START ORMA ---
if __name__ == "__main__":
    if "YOUR_API_KEY" in os.environ["GEMINI_API_KEY"]:
        print("❌ Error: Please set your Gemini API Key in line 7")
        exit()

    print("🧠 Orma V3 (Gemini Flash Edition) Initializing...")
    
    # Initialize Engine
    engine = OrmaEngine(llm_function=gemini_caller)
    
    # ✅ FIX 3: Force load existing memory to prove it works
    node_count = engine.ltm.graph.number_of_nodes()
    print(f"📂 Loaded Graph Memory: {node_count} nodes found in 'orma_memory.json'")
    
    print("\n✅ System Ready. Say 'exit' to quit.")
    
    while True:
        try:
            user_in = input("\nYou: ")
            if user_in.lower() in ["exit", "quit"]: 
                break
            
            engine.process(user_in)
            
        except KeyboardInterrupt:
            break
            
    print("👋 Shutting down.")