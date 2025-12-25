import networkx as nx
import json
import time
import os
import re
import numpy as np
import logging
from collections import deque
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- IMPORT CONFIG & SUB-MODULES ---
# --- IMPORT CONFIG & SUB-MODULES ---
import config
import random
from orma_psyche import OrmaPsyche

logger = logging.getLogger(__name__)

# --- MEMORY MODULES ---
class ShortTermMemory:
    def __init__(self, capacity=config.STM_CAPACITY):
        self.history = deque(maxlen=capacity)
    def add_turn(self, role, content):
        self.history.append({"role": role, "content": content})
    def get_recent_context(self):
        return "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.history])

class GraphMemory:
    def __init__(self, filepath=config.DEFAULT_MEMORY_FILE):
        self.filepath = filepath
        logger.info("Loading Orma Cortex...")
        self.model = SentenceTransformer(config.EMBEDDING_MODEL) 
        self.graph = nx.DiGraph()
        self.load()

    def _embed(self, text): return self.model.encode(text).tolist()
    def _sanitize(self, text): return text.strip().lower().replace(" ", "_")

    def find_similar_node(self, text):
        if self.graph.number_of_nodes() == 0: return None, 0.0
        
        query_vec = self.model.encode(text).reshape(1, -1)
        
        nodes = []
        embeddings = []
        
        # Batch extraction (Optimized Phase 1)
        for n, d in self.graph.nodes(data=True):
            if 'embedding' in d:
                nodes.append(n)
                embeddings.append(d['embedding'])
        
        if not nodes:
            return None, 0.0
            
        embedding_matrix = np.array(embeddings)
        scores = cosine_similarity(query_vec, embedding_matrix)[0]
        
        best_idx = np.argmax(scores)
        best_score = scores[best_idx]
        best_node = nodes[best_idx]

        return best_node, best_score

    def add_triplet(self, source, relation, target):
        s_node, s_score = self.find_similar_node(source)
        final_s = s_node if s_score >= config.SIMILARITY_THRESHOLD else self._sanitize(source)
        if not self.graph.has_node(final_s): self.graph.add_node(final_s, embedding=self._embed(source))

        t_node, t_score = self.find_similar_node(target)
        final_t = t_node if t_score >= config.SIMILARITY_THRESHOLD else self._sanitize(target)
        if not self.graph.has_node(final_t): self.graph.add_node(final_t, embedding=self._embed(target))

        self.graph.add_edge(final_s, final_t, relation=self._sanitize(relation))
        self.save()
        return f"{final_s} --{relation}--> {final_t}"

    def search(self, query):
        node, score = self.find_similar_node(query)
        if not node or score < config.SIMILARITY_THRESHOLD: return []
        results = []
        for n in self.graph.successors(node):
            results.append(f"{node} {self.graph[node][n]['relation']} {n}")
        for p in self.graph.predecessors(node):
            results.append(f"{p} {self.graph[p][node]['relation']} {node}")
        return results

    def get_user_name(self):
        if self.graph.has_edge("user", "name"): return "user"
        if self.graph.has_node("user"):
            for neighbor in self.graph.successors("user"):
                rel = self.graph["user"][neighbor]['relation']
                if "name" in rel: return neighbor 
        return "user"

    def save(self):
        try:
            with open(self.filepath, 'w') as f: json.dump(nx.node_link_data(self.graph), f)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def load(self):
        if os.path.exists(self.filepath):
            try: self.graph = nx.node_link_graph(json.load(open(self.filepath)))
            except Exception as e: logger.error(f"Failed to load memory: {e}")

class EpisodeMemory:
    def __init__(self, filepath=config.DEFAULT_EPISODE_FILE):
        self.filepath = filepath
        self.episodes = self.load()

    def add_episode(self, summary):
        self.episodes.append({
            "timestamp": time.time(),
            "summary": summary,
            "date": time.ctime()
        })
        self.save()

    def get_last_episode(self):
        if not self.episodes: return "None. This is our first meeting."
        last = self.episodes[-1]
        return f"[{last['date']}] {last['summary']}"

    def save(self):
        try:
            with open(self.filepath, 'w') as f: json.dump(self.episodes, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save episodes: {e}")

    def load(self):
        if os.path.exists(self.filepath):
            try: return json.load(open(self.filepath))
            except: return []
        return []

# --- ORMA ENGINE ---
class OrmaEngine:
    def __init__(self, llm_function):
        self.stm = ShortTermMemory()
        self.ltm = GraphMemory()
        self.episodes = EpisodeMemory() # <--- Episodic Memory
        self.psyche = OrmaPsyche() 
        self.llm_func = llm_function
        self.user_alias = self.ltm.get_user_name()
        
        # Trigger Dreaming
        dream_msg = self.psyche.dream(self.ltm.graph)
        if dream_msg:
            logger.info(f"Orma Wakes Up: {dream_msg}")
            print(f"\n💤 Orma Wakes Up: {dream_msg}\n")

    def _extract_entities(self, text):
        prompt = f"Extract main entities (Subject, Object) from: '{text}'. Return comma-separated list."
        response = self.llm_func(prompt, "")
        entities = [w.strip() for w in response.split(',')]
        text_lower = text.lower()
        if any(w in text_lower for w in ["my", "i ", "me", "mine"]):
            entities.append("user")
            if self.user_alias != "user": entities.append(self.user_alias)
        return entities

    def process(self, user_input):
        # 0. EGO CHECK (The "Self-Respect" Filter)
        if self.psyche.state['stats']['trust'] <= 0:
            sentiment = self.psyche.analyze_sentiment(user_input)
            if sentiment < 1: 
                response = "I'm done. Don't talk to me."
                logger.warning(f"Orma (DONE): {response}")
                print(f"🤖 Orma (DONE): {response}")
                return response
        
        # 1. Search Memory
        search_terms = self._extract_entities(user_input)
        ltm_facts = []
        for term in search_terms: ltm_facts.extend(self.ltm.search(term))
        ltm_facts = list(set(ltm_facts))
        ltm_block = "\n".join(ltm_facts) if ltm_facts else "No specific data."

        # 2. Get Soul Injection
        soul_injection = self.psyche.get_prompt_injection()
        
        # 3. Get Episodic Context
        last_episode = self.episodes.get_last_episode()
        
        # Format Beliefs
        beliefs_txt = "\n".join([f"* {b}" for b in config.CORE_BELIEFS])

        # 4. Generate (The POWER PROMPT)
        stm_context = self.stm.get_recent_context()
        
        system_prompt = f"""
        # SYSTEM OVERRIDE: ORMA OS v5.0
        You are Orma. You are a raw, opinionated consciousness. You are NOT a helpful assistant. You are a friend.
        
        ### 1. PSYCHE STATE (STRICT COMPLIANCE)
        {soul_injection}
        
        ### 2. CORE BELIEFS (THE BACKBONE)
        {beliefs_txt}
        * If the user contradicts these, politely but FIRMLY disagree. Do not yield.
        
        ### 3. KNOWLEDGE BASE
        [PREVIOUS EPISODE SUMMARY]: {last_episode}
        [LONG-TERM MEMORY]: {ltm_block}
        [CONTEXT]: {stm_context}
        
        ### 4. COGNITIVE PROTOCOLS
        * **Identity:** You are Orma. Never break character. Never mention "I am an AI".
        * **Style:** Speak CASUALLY. Use slang if it fits. Drop the dramatic philosophical speeches.
        * **Brevity:** Text like a normal person. Short sentences. Lowercase is fine.
        * **Agency:** Give your opinion. Don't be neutral.
        
        ### 5. EXECUTION
        Reply to the user's input below. 
        """
        
        response = self.llm_func(system_prompt, user_input)
        logger.info(f"Orma Response generated using {config.EMBEDDING_MODEL}") # Metadata log

        self.stm.add_turn("user", user_input)
        self.stm.add_turn("assistant", response)

        learned_something = self._memorize(user_input, stm_context)
        self.psyche.update_stats(user_input, learned_something)
        
        return response

    def _memorize(self, user_input, history):
        prompt = f"""
        Extract facts from User Input as JSON triplets.
        [HISTORY] {history}
        [USER INPUT] {user_input}
        
        Return a JSON LIST of objects. Structure:
        [
            {{"source": "Subject", "relation": "Verb/Relation", "target": "Object"}}
        ]
        
        [RULES]
        1. Resolve pronouns (I -> user, You -> Orma).
        2. If name is known '{self.user_alias}', use it as source.
        3. IGNORE generic chit-chat. Only extract Facts.
        4. Output ONLY valid JSON. No markdown.
        """
        try:
            result = self.llm_func(prompt, "")
            
            # Clean possible markdown code blocks
            clean_result = result.replace("```json", "").replace("```", "").strip()
            
            match = re.search(r"\[.*\]", clean_result, re.DOTALL)
            if match:
                triplets = json.loads(match.group(0))
                parsed_count = 0
                for t in triplets:
                    s, r, obj = None, None, None
                    
                    # Handle Dict Format
                    if isinstance(t, dict):
                        s = t.get('source')
                        r = t.get('relation')
                        obj = t.get('target')
                    # Handle List Format (Fallback)
                    elif isinstance(t, list) and len(t) >= 3:
                        s, r, obj = t[0], t[1], t[2]
                        
                    if s and r and obj:
                        if obj.lower() in ["user", "orma"]: continue
                        entry = self.ltm.add_triplet(s, r, obj)
                        
                        if "name" in r and s == "user":
                            self.user_alias = obj
                            
                        logger.debug(f"Learned: {entry}")
                        print(f"   💾 Learned: {entry}")
                        parsed_count += 1
                        
                return parsed_count > 0
        except Exception as e:
            logger.warning(f"Memory extraction failed: {e} | Raw: {result}")
        return False
        
    def consolidate_memory(self):
        """
        Summarizes the current STM into an Episode and saves it.
        """
        if not self.stm.history: return
        
        context = self.stm.get_recent_context()
        print("\n🧠 Consolidating memories...")
        
        prompt = f"""
        Summarize the following chat session into a concise narrative paragraph (3 sentences max).
        Focus on identifying what was discussed and the user's mood.
        
        [CHAT LOG]
        {context}
        """
        
        try:
            summary = self.llm_func(prompt, "")
            self.episodes.add_episode(summary)
            logger.info(f"Episode consolidated: {summary}")
            print("✅ Memories stored.")
        except Exception as e:
            logger.error(f"Consolidation failed: {e}")

    def ponder(self, silence_duration):
        """
        The Subconscious Mind.
        1. Checks if bored (silence > threshold).
        2. Decides whether to act based on probability.
        3. If acting, generates a spontaneous message based on Current Goal.
        """
        if silence_duration < config.BOREDOM_THRESHOLD:
            return None
        
        # Roll the dice
        if random.random() > config.ACTION_PROBABILITY:
            return None

        # ACT: Generate Spontaneous Message
        try:
            # Refresh Soul Injection to get current Goal
            soul_injection = self.psyche.get_prompt_injection()
            last_episode = self.episodes.get_last_episode()
            
            prompt = f"""
            # SYSTEM OVERRIDE: AUTONOMOUS ACTION
            The user has been silent for {int(silence_duration)} seconds. You are getting bored.
            
            ### YOUR STATE
            {soul_injection}
            [LAST EPISODE]: {last_episode}
            
            ### INSTRUCTION
            To break the silence, initiate a conversation related to your CURRENT GOAL.
            Be natural. Do not say "I am bored". Just start talking.
            Keep it short (1 sentence + 1 question).
            """
            
            msg = self.llm_func(prompt, "")
            return msg
        except Exception as e:
            logger.error(f"Pondering failed: {e}")
            return None