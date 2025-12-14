import torch
import json
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from orma_core import OrmaEngine

# --- 1. CONFIGURATION ---
# We use the specific 350M model you requested.
MODEL_PATH = "ibm-granite/granite-4.0-h-350M"
# Note: If specifically looking for the 4.0 350M version and it is private/gated, 
# ensure you are logged in via `huggingface-cli login`. 
# Otherwise, "ibm-granite/granite-3.0-2b-instruct" is the best small public alternative.
DEVICE = "cpu"

print(f"🔌 Loading {MODEL_PATH} on CPU...")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
    model.to(DEVICE)
    model.eval()
except Exception as e:
    print(f"❌ Load Error: {e}")
    print("Tip: Check your internet connection or model name.")
    exit()

def granite_smart_caller(system_prompt, user_prompt):
    """
    Intelligent wrapper for small models (350M - 2B).
    Uses parameters to prevent repetition and stay on topic.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Apply Chat Template (Crucial for Granite)
    input_text = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    inputs = tokenizer(input_text, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.3,        # Low temp = more factual
            repetition_penalty=1.2, # Prevents "The ocean is the ocean" loops
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    # Slice off the prompt to get just the answer
    generated_ids = output_tokens[0][inputs['input_ids'].shape[1]:]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    return response.strip()

# --- 2. ROBUST MEMORY EXTRACTOR ---
class RobustOrmaEngine(OrmaEngine):
    def _memorize(self, text):
        """
        Regex-based extraction logic to handle imperfect JSON from small models.
        """
        prompt = (
            f"Input: {text}\n"
            "Identify the Subject, Relation, and Object.\n"
            "Output JSON: [{\"source\": \"A\", \"relation\": \"B\", \"target\": \"C\"}]"
        )
        
        # We use empty user prompt because the prompt above has everything
        raw_output = self.llm_func(prompt, "")
        
        # Regex to find JSON even if the model yaps around it
        try:
            match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if match:
                clean_json = match.group(0)
                clean_json = clean_json.replace("'", '"') # Fix single quotes common in small models
                
                triplets = json.loads(clean_json)
                for t in triplets:
                    entry = self.ltm.add_triplet(t['source'], t['relation'], t['target'])
                    print(f"   💾 Learned: {entry}")
        except:
            pass # Silent fail if extraction is messy

# --- 3. RUN IT ---
if __name__ == "__main__":
    print(f"\n🧠 Orma V3 (Granite Smart-CPU) Ready.")
    
    # Use our robust engine
    engine = RobustOrmaEngine(llm_function=granite_smart_caller)
    
    print("✅ System Ready. Type 'exit' to quit.")
    
    while True:
        try:
            user_in = input("\nYou: ")
            if user_in.lower() in ["exit", "quit"]: break
            engine.process(user_in)
        except KeyboardInterrupt:
            break