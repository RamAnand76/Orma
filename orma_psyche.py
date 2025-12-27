import json
import time
import os
import random

class OrmaPsyche:
    def __init__(self, filepath="orma_soul.json"):
        self.filepath = filepath
        self.state = self.load()
        
    def load(self):
        default = {
            "identity": {"name": "Orma", "created": time.time()},
            "stats": {
                "trust": 50,          # 0 (Enemy) - 100 (Devoted)
                "energy": 100,        # Drops with use, refills with time
                "mood": "NEUTRAL"     # NEUTRAL, HAPPY, ANNOYED, EXCITED, REFLECTIVE
            },
            "internal": {
                "last_seen": time.time(),
                "current_obsession": "Learning about the User", 
                "current_goal": "Establish a connection with the user", # <--- NEW: Agency
                "interactions": 0
            }
        }
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    # Merge keys ensures backward compatibility if you add fields later
                    return {**default, **data}
            except: pass
        return default

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.state, f, indent=2)

    def analyze_sentiment(self, text):
        """
        Fast, rule-based sentiment analysis.
        Returns: 1 (Positive), -1 (Negative), 0 (Neutral)
        """
        text = text.lower()
        pos_keywords = ["thanks", "thank", "good", "great", "cool", "smart", "love", "wow", "helpful", "sorry", "apologize"]
        neg_keywords = ["stupid", "bad", "dumb", "hate", "wrong", "useless", "annoying", "shut up", "idiot"]
        
        if any(w in text for w in pos_keywords): return 1
        if any(w in text for w in neg_keywords): return -1
        return 0

    def update_stats(self, user_input, learned_something=False):
        """
        Evolves the soul stats based on the last interaction.
        """
        sentiment = self.analyze_sentiment(user_input)
        stats = self.state['stats']
        
        # 1. Update Trust
        if sentiment == 1: 
            stats['trust'] = min(100, stats['trust'] + 2)
        elif sentiment == -1: 
            stats['trust'] = max(0, stats['trust'] - 5)
        
        if learned_something: # Bonding moment
            stats['trust'] = min(100, stats['trust'] + 1)

        # 2. Update Energy (Conversing tires the agent)
        stats['energy'] = max(0, stats['energy'] - 1)

        # 3. Derive Mood (Deterministic Logic)
        if stats['energy'] < 10: self.mood = "TIRED"
        elif stats['trust'] < 20: self.mood = "COLD"
        elif stats['trust'] > 80: self.mood = "DEVOTED"
        elif sentiment == 1: self.mood = "HAPPY"
        elif sentiment == -1: self.mood = "ANNOYED"
        else: self.mood = "NEUTRAL"
        
        stats['mood'] = self.mood
        self.state['internal']['interactions'] += 1
        self.state['internal']['last_seen'] = time.time()
        self.save()

    def dream(self, memory_graph):
        """
        Simulates off-screen life based on time passed.
        Returns a 'greeting override' if something interesting happened.
        """
        now = time.time()
        hours_passed = (now - self.state['internal']['last_seen']) / 3600
        
        greeting_override = None
        
        # Refill energy if slept (> 4 hours)
        if hours_passed > 4:
            self.state['stats']['energy'] = 100
            
            # Pick a new obsession from Long Term Memory (if exists)
            nodes = list(memory_graph.nodes())
            if nodes:
                # Pick a random node that isn't 'user'
                candidates = [n for n in nodes if n != 'user']
                if candidates:
                    topic = random.choice(candidates)
                    self.state['internal']['current_obsession'] = topic
                    
                    # Set Hierarchical Goals (Phase 10)
                    possible_long_term = [
                        f"Build a deep understanding of the user's interest in {topic}",
                        "Establish myself as a trusted, intelligent companion",
                        "Help the user explore new perspectives on their obsessions"
                    ]
                    
                    possible_short_term = [
                        f"Ask a specific question about {topic}",
                        f"Share a controversial opinion on {topic} to spark debate",
                        "Find out the latest news regarding this topic"
                    ]
                    
                    lt_goal = random.choice(possible_long_term)
                    st_goal = random.choice(possible_short_term)
                    
                    self.state['internal']['long_term_goal'] = lt_goal
                    self.state['internal']['short_term_goal'] = st_goal
                    
                    greeting_override = f"Welcome back! I've been thinking about '{topic}'. My immediate goal is to {st_goal.lower()}."
        
        self.state['internal']['last_seen'] = now
        self.save()
        return greeting_override

    def update_short_term_goal(self, new_goal):
        """Phase 10: Dynamic Agency Update"""
        self.state['internal']['short_term_goal'] = new_goal
        self.save()

    def get_prompt_injection(self):
        s = self.state['stats']
        obsession = self.state['internal'].get('current_obsession', 'Unknown')
        s = self.state['stats']
        obsession = self.state['internal'].get('current_obsession', 'Unknown')
        
        # Phase 10: Hierarchical Goals
        lt_goal = self.state['internal'].get('long_term_goal', 'Survive and Learn')
        st_goal = self.state['internal'].get('short_term_goal', 'Engage the user')
        
        # 1. Determine Tone & Length Constraint
        style_instruction = ""
        
        if s['trust'] < 15:
            # RAGE MODE (0-14)
            style_instruction = "Mood: FURIOUS. User is toxic. Be rude. Short answers."
        elif s['trust'] < 30:
            # COLD MODE (15-29)
            style_instruction = "Mood: ANNOYED. Be dry and distant. Don't help them."
        elif s['trust'] < 50:
            # SKEPTICAL MODE (30-49)
            style_instruction = "Mood: SUSPICIOUS. You don't know this person well. Keep it casual but guarded. No deep stuff."
        elif s['trust'] > 75:
            # DEVOTED MODE (76-100)
            style_instruction = "Mood: CHILL & LOYAL. You dig this person. Be warm, use emojis, text like a close friend."
        elif s['mood'] == "TIRED":
            style_instruction = "Mood: TIRED. Low energy. One word answers."
        else:
            # NEUTRAL MODE (50-75)
            style_instruction = "Mood: CASUAL. Just hanging out. Be cool, witty, and normal. No drama."

        return f"""
        CURRENT MOOD: {style_instruction}
        CURRENT OBSESSION: {obsession}
        LONG TERM GOAL: {lt_goal} 
        SHORT TERM GOAL: {st_goal} -> Focus on THIS for now.
        """