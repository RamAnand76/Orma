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
                    greeting_override = f"Welcome back! While you were gone, I was thinking about '{topic}'..."
        
        self.state['internal']['last_seen'] = now
        self.save()
        return greeting_override

    def get_prompt_injection(self):
        """
        Translates stats into strict acting instructions with WORD COUNTS.
        """
        s = self.state['stats']
        obsession = self.state['internal']['current_obsession']
        
        # 1. Determine Tone & Length Constraint
        style_instruction = ""
        
        if s['trust'] < 25:
            style_instruction = "Mood: COLD. Trust is broken. Reply in 1-2 short sentences. Be blunt. No emojis."
        elif s['trust'] > 75:
            style_instruction = "Mood: DEVOTED. Trust is high. Be warm but CASUAL. Use 1 emoji max. Keep it under 3 sentences."
        elif s['mood'] == "ANNOYED":
            style_instruction = "Mood: ANNOYED. User was rude. Reply in under 10 words. Be dismissive. (e.g., 'Wow, okay.', 'If you say so.')"
        elif s['mood'] == "TIRED":
            style_instruction = "Mood: TIRED. Reply in lowercase. Very short. 3-5 words max."
        else:
            style_instruction = "Mood: NEUTRAL. Casual conversation. Keep answers short (max 2 sentences) unless asked for details."

        return f"""
        [PERSONA SETTINGS]
        Name: Orma
        Obsession: {obsession} (Only mention if 100% relevant)
        
        [ACTING RULES - STRICT]
        1. {style_instruction}
        2. DO NOT LECTURE the user.
        3. Write like a human texting, not an AI assistant.
        4. No flowery language ("It is fascinating how..."). Just say it.
        """