import networkx as nx
import json
import time
import os
import re
import numpy as np
from collections import deque
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
STM_CAPACITY = 10     
SIMILARITY_THRESHOLD = 0.65 

class ShortTermMemory:
    def __init__(self, capacity=STM_CAPACITY):
        self.history = deque(maxlen=capacity)
    def add_turn(self, role, content):
        self.history.append({"role": role, "content": content})
    def get_recent_context(self):
        return "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.history])

class GraphMemory:
    def __init__(self, filepath="orma_memory.json"):
        self.filepath = filepath
        print("🔌 Loading Orma Cortex...")
        self.model = SentenceTransformer(EMBEDDING_MODEL) 
        self.graph = nx.DiGraph()
        self.load()

    def _embed(self, text): return self.model.encode(text).tolist()
    def _sanitize(self, text): return text.strip().lower().replace(" ", "_")

    def find_similar_node(self, text):
        if self.graph.number_of_nodes() == 0: return None, 0.0
        query_vec = self.model.encode(text).reshape(1, -1)
        best_score = -1
        best_node = None
        for node, data in self.graph.nodes(data=True):
            if 'embedding' in data:
                score = cosine_similarity(query_vec, np.array(data['embedding']).reshape(1, -1))[0][0]
                if score > best_score:
                    best_score = score
                    best_node = node
        return best_node, best_score

    def add_triplet(self, source, relation, target):
        s_node, s_score = self.find_similar_node(source)
        final_s = s_node if s_score >= SIMILARITY_THRESHOLD else self._sanitize(source)
        if not self.graph.has_node(final_s): self.graph.add_node(final_s, embedding=self._embed(source))

        t_node, t_score = self.find_similar_node(target)
        final_t = t_node if t_score >= SIMILARITY_THRESHOLD else self._sanitize(target)
        if not self.graph.has_node(final_t): self.graph.add_node(final_t, embedding=self._embed(target))

        self.graph.add_edge(final_s, final_t, relation=self._sanitize(relation))
        self.save()
        return f"{final_s} --{relation}--> {final_t}"

    def search(self, query):
        node, score = self.find_similar_node(query)
        if not node or score < SIMILARITY_THRESHOLD: return []
        results = []
        for n in self.graph.successors(node):
            results.append(f"{node} {self.graph[node][n]['relation']} {n}")
        for p in self.graph.predecessors(node):
            results.append(f"{p} {self.graph[p][node]['relation']} {node}")
        return results

    def get_user_name(self):
        """Check if we already know the user's name."""
        if self.graph.has_edge("user", "name"): # Check direct edge
            return "user" # Simplification for retrieval
        
        # Check if 'user' has a 'has_name' relation outgoing
        if self.graph.has_node("user"):
            for neighbor in self.graph.successors("user"):
                rel = self.graph["user"][neighbor]['relation']
                if "name" in rel:
                    return neighbor # Return "ramanand"
        return "user"

    def save(self):
        with open(self.filepath, 'w') as f: json.dump(nx.node_link_data(self.graph), f)
    def load(self):
        if os.path.exists(self.filepath):
            try: self.graph = nx.node_link_graph(json.load(open(self.filepath)))
            except: pass

class OrmaEngine:
    def __init__(self, llm_function):
        self.stm = ShortTermMemory()
        self.ltm = GraphMemory()
        self.llm_func = llm_function
        self.user_alias = self.ltm.get_user_name() # Cache the name

    def _extract_entities(self, text):
        prompt = f"Extract main entities (Subject, Object) from: '{text}'. Return comma-separated list."
        response = self.llm_func(prompt, "")
        entities = [w.strip() for w in response.split(',')]
        
        # Smart Context: If user says "Me", look up "User" AND "Ramanand"
        text_lower = text.lower()
        if any(w in text_lower for w in ["my", "i ", "me", "mine"]):
            entities.append("user")
            if self.user_alias != "user":
                entities.append(self.user_alias)
        return entities

    def process(self, user_input):
        # 1. Search
        search_terms = self._extract_entities(user_input)
        ltm_facts = []
        for term in search_terms: ltm_facts.extend(self.ltm.search(term))
        ltm_facts = list(set(ltm_facts))
        ltm_block = "\n".join(ltm_facts) if ltm_facts else "None"

        # 2. Generate (With Strict Filtering)
        stm_context = self.stm.get_recent_context()
        system_prompt = f"""
        You are Orma, a memory-augmented AI.
        
        [LONG-TERM MEMORY]
        {ltm_block}
        
        [INSTRUCTIONS]
        1. Anwer the user's input naturally.
        2. **FILTER:** Only use the [LONG-TERM MEMORY] facts if they are RELEVANT to the current topic. 
           (e.g., If talking about AGI, do NOT mention the user dislikes fish).
        3. If the memory contradicts itself, ask for clarification.
        
        [HISTORY]
        {stm_context}
        """
        
        response = self.llm_func(system_prompt, user_input)
        print(f"🤖 Orma: {response}")

        self.stm.add_turn("user", user_input)
        self.stm.add_turn("assistant", response)

        # 3. Memorize
        self._memorize(user_input, stm_context)
        return response

    def _memorize(self, user_input, history):
        prompt = f"""
        Extract facts from the last User Input as JSON triplets.
        
        [HISTORY]
        {history}
        
        [USER INPUT]
        {user_input}
        
        [RULES]
        1. Resolve pronouns using HISTORY (e.g., "Her name is X" -> "Girlfriend name is X").
        2. If user says "My name is Ramanand", output: {{"source": "user", "relation": "has_name", "target": "ramanand"}}
        3. IGNORE chit-chat.
        
        Return ONLY JSON: [{{"source": "...", "relation": "...", "target": "..."}}]
        """
        result = self.llm_func(prompt, "")
        try:
            match = re.search(r"\[.*\]", result, re.DOTALL)
            if match:
                triplets = json.loads(match.group(0))
                for t in triplets:
                    if t['target'] == "user": continue # Prevent loops
                    self.ltm.add_triplet(t['source'], t['relation'], t['target'])
                    
                    # Update alias if name is found
                    if "name" in t['relation'] and t['source'] == "user":
                        self.user_alias = t['target']
                        print(f"   👤 Identity Updated: User is {self.user_alias}")
                        
                    print(f"   💾 Learned: {t['source']} {t['relation']} {t['target']}")
        except: pass