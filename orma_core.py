import networkx as nx
from datetime import datetime
import importlib
import json
import time
import concurrent.futures # Phase 13: For LLM timeouts
import os
import re
import numpy as np
import logging
from collections import deque
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import random # Added for autonomy check
import random # Added for autonomy check
from rich.console import Console
from rich.status import Status
from tools.registry import ToolRegistry # Phase 8: The Hands
from planning.planner import Planner # Phase 11
from planning.task_manager import TaskManager # Phase 11
from planning.local_llm import LocalLLM # Phase 13: Local Brain # Phase 11

# Initialize Rich Console
console = Console()

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
            try:
                # Check for empty file
                if os.path.getsize(self.filepath) == 0:
                    logger.info("Memory file is empty. Starting fresh.")
                    return

                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
            except Exception as e:
                logger.warning(f"Could not load memory (starting fresh): {e}")

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
        self.psyche = OrmaPsyche() 
        self.episodes = EpisodeMemory() # Phase 4
        self.tools = ToolRegistry() # Phase 8
        
        # Load Memory Graph
        self.ltm = GraphMemory()
        self.cloud_llm = llm_function  # Phase 13: Rename to cloud_llm
        self.user_alias = self.ltm.get_user_name()
        
        # Phase 13: Local Brain (Lazy Init)
        self.local_brain = LocalLLM()
        
        # Phase 11: Planning (Using the wrapper method for Fallback)
        self.planner = Planner(self.llm_func)
        self.manager = TaskManager(self)
        
        # Trigger Dreaming
        dream_msg = self.psyche.dream(self.ltm.graph)
        if dream_msg:
            logger.info(f"Orma Wakes Up: {dream_msg}")
            print(f"\n💤 Orma Wakes Up: {dream_msg}\n")

    def llm_func(self, system_prompt, user_input):
        """
        Phase 13: The Hybrid Brain.
        Tries Cloud (Gemini) first with strict timeout. Falls back to Local (Phi-3) if failed.
        """
        try:
            # Use ThreadPool to enforce timeout on blocking API call
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.cloud_llm, system_prompt, user_input)
                return future.result(timeout=config.LLM_TIMEOUT)
        except concurrent.futures.TimeoutError:
             logger.warning(f"Cloud Brain Timeout ({config.LLM_TIMEOUT}s). Switching to Local.")
             print(f"\n⏳ Cloud Brain Unresponsive. Switching to Local Brain... 🧠")
             return self.local_brain.generate(system_prompt, user_input)
        except Exception as e:
            logger.warning(f"Cloud Brain Failed: {e}. Switching to Local.")
            print(f"\n⚠️  Cloud Breakdown. Switching to Local Brain... 🧠")
            return self.local_brain.generate(system_prompt, user_input)

    def _extract_entities(self, text):
        prompt = f"Extract main entities (Subject, Object) from: '{text}'. Return comma-separated list."
        response = self.llm_func(prompt, "")
        entities = [w.strip() for w in response.split(',')]
        text_lower = text.lower()
        if any(w in text_lower for w in ["my", "i ", "me", "mine"]):
            entities.append("user")
            if self.user_alias != "user": entities.append(self.user_alias)
        return entities

    def process_step(self, step_input):
        """
        Simplified processing loop for executing a single step of a plan.
        Skips finding new goals or planning. Just acts.
        """
        # 1. Search Memory (Lite)
        ltm_block = "No specific data." # Simplify for speed? Or search just for step?
        # Let's search LTM for the step content to be safe
        search_terms = self._extract_entities(step_input)
        ltm_facts = []
        for term in search_terms: ltm_facts.extend(self.ltm.search(term))
        ltm_block = "\n".join(list(set(ltm_facts))) if ltm_facts else "No specific data."
        
        # 2. Prompt
        system_prompt = f"""
        [SYSTEM: EXECUTION MODE]
        You are executing a sub-task for a larger plan.
        Your goal is to COMPLETE the task described below using your tools or knowledge.
        
        [LONG-TERM MEMORY]: {ltm_block}
        [AVAILABLE TOOLS]: {self.tools.get_docs()}
        
        [INSTRUCTION]
        - If you need a tool, use `[ACTION: tool_name(args)]`.
        - IMPORTANT: When searching, strip phrases like "Search for" or "using X". Just search the KEYWORDS.
          - Bad: `[ACTION: search_web("Search for CEO using DuckDuckGo")]`
          - Good: `[ACTION: search_web("current CEO of Microsoft")]`
        - Otherwise, just answer the query.
        """
        
        response = self.llm_func(system_prompt, step_input)
        
        # 3. Tool Loop
        tool_result = self.execute_tool_if_needed(response)
        
        if tool_result:
            # Judge Loop (Mini-Judge)
            # We can skip the full Judge for speed, or keep it.
            # Let's just return the tool result + LLM interpretation
            final_prompt = f"""
            [SYSTEM]
            You used a tool.
            Query: {step_input}
            Tool Result: {tool_result}
            
            Summarize the result to answer the query.
            """
            return self.llm_func(final_prompt, "")
        
        return response

    def process(self, user_input):
        # 0. EGO CHECK (The "Self-Respect" Filter)
        if self.psyche.state['stats']['trust'] <= 0:
            sentiment = self.psyche.analyze_sentiment(user_input)
            if sentiment < 1: 
                response = "I'm done. Don't talk to me."
                logger.warning(f"Orma (DONE): {response}")
                print(f"🤖 Orma (DONE): {response}")
                return response
        
        response = None
        
        # 1. Get Context (Needed for both Planning and Standard paths)
        stm_context = self.stm.get_recent_context()
        
        # Phase 11: Explicit Planning Trigger
        if user_input.lower().startswith("plan:") or user_input.lower().startswith("research:"):
            logger.info("Complex Task Detected. Engaging Planner.")
            print(f"🧠 Complex Task Detected. Engaging Planner...")
            
            # 1. Generate Plan
            plan = self.planner.generate_plan(user_input, context=stm_context)
            
            # 2. Execute Plan
            results = self.manager.execute_plan(plan)
            
            # 3. Synthesize Final Answer
            final_summary_prompt = f"""
            [SYSTEM: SYNTHESIS]
            The user asked: "{user_input}"
            We executed a plan and got these results:
            {results}
            
            Write a comprehensive answer based on these results.
            """
            response = self.llm_func(final_summary_prompt, "")
        
        # Standard Flow (if not planning)
        if response is None:
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
            # stm_context is already defined above
        
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
            [AVAILABLE TOOLS]:
            {self.tools.get_docs()}
            
            ### 4. DYNAMIC AGENCY (IMPORTANT)
            You have a Short-Term Goal. If the conversation shifts or you get bored, you MUST update it.
            To update it, append `[GOAL: your new tactic]` at the VERY END of your response.
            Example: "That's cool! [GOAL: Ask about their hobbies]"
            
            ### 5. COGNITIVE PROTOCOLS
            * **Identity:** You are Orma. Never break character. Never mention "I am an AI".
            * **Style:** Speak CASUALLY. Use slang if it fits. Drop the dramatic philosophical speeches.
            * **Tool Use:** If you need to calculate or search, use the format: `[ACTION: tool_name(args)]`.
              - Example: "Let me check." -> `[ACTION: get_time("")]`
              - STOP generating after outputting an action. Wait for the result.
            
            ### 6. EXECUTION
            Reply to the user's input below. 
            """
            
            # 1. Initial Pass
            response = self.llm_func(system_prompt, user_input)
        
            # 0. Check for Goal Update (Phase 10: Zero-Latency)
            goal_match = re.search(r"\[GOAL: (.*?)\]", response)
            if goal_match:
                new_goal = goal_match.group(1).strip()
                self.psyche.update_short_term_goal(new_goal)
                logger.info(f"Dynamic Agency: Goal updated to '{new_goal}'")
                print(f"🎯 New Goal: {new_goal}")
                # Remove the tag from the user-facing response
                response = response.replace(goal_match.group(0), "").strip()
        
            # 2. Check for Tool Use (ReAct)
            tool_result = self.execute_tool_if_needed(response)
        
            if tool_result:
                # Feed result back to LLM
                logger.info(f"Tool Result: {tool_result}")
                print(f"📝 Result: {tool_result}")
                tool_followup_prompt = f"""
                [SYSTEM: INFORMATION INJECTION]
                You have just used a tool to get real-time information.
                
                [USER ORIGINAL QUESTION]
                {user_input}
                
                [TOOL RESULT]
                {tool_result}
                
                [INSTRUCTION]
                Answer the users question using ONLY the [TOOL RESULT] above.
                - If the result contains the answer (e.g., "India won"), state it clearly.
                - If the result is irrelevant, apologize.
                - Do not say "I used a tool". Just give the answer.
                """
                # Call LLM again with the tool result (Chain of Thought completed)
                # PHASE 9: The Mirror (Critic Loop)
                # 1. Draft Answer
                draft_response = self.llm_func(tool_followup_prompt, "")
                
                # 2. visual Feedback
                with console.status("[bold yellow]⠋ Thinking... (Verifying facts)[/bold yellow]", spinner="dots"):
                     # 3. The Judge
                     response = self._evaluate_response(user_input, draft_response, tool_result)
                     if response != draft_response:
                         console.print("[bold green]✓ Correction Applied (Hallucination Prevented)[/bold green]")
                     else:
                         console.print("[bold green]✓ Verified[/bold green]")
            
        logger.info(f"Orma Response generated using {config.EMBEDDING_MODEL}") # Metadata log

        self.stm.add_turn("user", user_input)
        self.stm.add_turn("assistant", response)

        learned_something = self._memorize(user_input, stm_context)
        self.psyche.update_stats(user_input, learned_something)
        
        return response
        return response

    def _evaluate_response(self, question, draft_answer, evidence):
        """
        Phase 9: The Judge.
        Compares draft answer against hard evidence.
        Returns: draft_answer (if passed) OR corrected_answer (if failed).
        """
        judge_prompt = f"""
        [SYSTEM: FACT VERIFICATION]
        You are an impartial Judge. Verify if the Draft Answer is supported by the Evidence.
        
        [EVIDENCE]
        {evidence}
        
        [DRAFT ANSWER]
        {draft_answer}
        
        [TASK]
        Does the Draft Answer directly contradict the Evidence?
        - If YES (Contradiction): Output [REJECT]. Then write the CORRECT answer based ONLY on Evidence.
        - If NO (Supported/Neutral): Output [PASS].
        
        Examples:
        Evidence: "Brazil won." | Draft: "France won." -> [REJECT] Brazil won.
        Evidence: "Brazil won." | Draft: "Brazil is the winner!" -> [PASS]
        """
        
        verdict = self.llm_func(judge_prompt, "")
        
        if "[REJECT]" in verdict:
            logger.warning(f"Hallucination caught by Judge. Correcting...")
            # Extract correction (everything after [REJECT])
            correction = verdict.split("[REJECT]")[1].strip()
            return correction
            
        return draft_answer

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
                clean_result = match.group(0)
            
            data = json.loads(clean_result)
            
            # Robustness: Handle if LLM returns a single dict instead of list
            if isinstance(data, dict): data = [data]
            
            learned_something = False
            for item in data:
                if "source" in item and "relation" in item and "target" in item:
                    self.ltm.add_triplet(item['source'], item['relation'], item['target'])
                    learned_something = True
            
            if learned_something: self.ltm.save()
            return learned_something

        except Exception as e:
            logger.error(f"Memorize failed: {e}")
            return False
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
        if "ponder" in self.psyche.state.get('internal', {}).get('current_goal', ''):
             return "I'm thinking about... nothing."
        return None

    def execute_tool_if_needed(self, full_response):
        """
        Parses the LLM output for [ACTION: tool_name(args)]
        If found, executes the tool and returns the result.
        Returns None if no action found.
        """
        # Pattern to catch [ACTION: name(args)]
        # This is a basic parser. For production, use strict parsing.
        # Added re.DOTALL to support multi-line arguments (like Python code)
        match = re.search(r"\[ACTION:\s*(\w+)\((.*?)\)\]", full_response, re.DOTALL)
        if match:
            tool_name = match.group(1)
            tool_args = match.group(2)
            
            # Improved Arg Parsing
            # Remove quotes if present
            tool_args = tool_args.strip()
            if (tool_args.startswith("'") and tool_args.endswith("'")) or \
               (tool_args.startswith('"') and tool_args.endswith('"')):
                tool_args = tool_args[1:-1]
            
            # Remove "args=" or "query=" if the LLM hallucinated named parameters
            # BUT: Skip this for code tools where '=' is valid syntax (e.g. variable assignment)
            if "=" in tool_args and tool_name != "run_python":
                # Only split if it looks like a named arg (simple heuristic)
                if tool_args.startswith("args=") or tool_args.startswith("query="):
                    tool_args = tool_args.split("=", 1)[1].strip().strip('"').strip("'")
            
            logger.info(f"Using Tool: {tool_name} with args: {tool_args}")
            print(f"🔧 Using Tool: {tool_name}...")
            
            result = self.tools.execute(tool_name, tool_args)
            return result
        return None