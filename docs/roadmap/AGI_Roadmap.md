# 🗺️ The Orma AGI Roadmap

**Current Status:** Level 3 (Competent Agent)
**Version:** Orma OS v6.0 (Autonomous Edition)
**Date:** December 2025

---

## 🟢 COMPLETED STAGES (The Journey So Far)

### Level 1: The Chatbot (Foundations)
*Building a robust, personality-driven conversationalist.*
*   **Phase 1: Robustness:** Moving from spaghetti code to a modular Class-based architecture. Added logging and error handling.
*   **Phase 2: Reliability:** Implementing retry logic and fixing context window overflows.
*   **Phase 3: Personality:** Giving Orma a "Soul" (Moods, Trust Score, Obsessions). Breaking the "As an AI..." filter.

### Level 2: The Emergent Mind (Memory & Autonomy)
*Moving beyond the session limit. The AI begins to "live" off-screen.*
*   **Phase 4: Episodic Memory:** Implementing `EpisodeMemory` so Orma remembers past conversations.
*   **Phase 5: Agency & Alignment:** Introduction of the "Psyche" – internal state that evolves independently of user input (Energy, Trust).
*   **Phase 6: The Autonomous Loop:** The "Dreaming" system. Orma simulates thoughts and updates its state when the user is away.
*   **Phase 7: True Humanization:** Refining the output style to be raw, opinionated, and unpredictable.

### Level 3: The Competent Agent (Proto-AGI) 📍 **[WE ARE HERE]**
*The AI gains hands, eyes, and self-awareness. It can act on the world.*
*   **Phase 8: The Hands (Tool Use):** Integration of Web Search (`ddgs`) and System Tools. Orma can research real-time facts.
*   **Phase 9: The Mirror (Metacognition):** The "Critic Loop". Orma critiques its own draft answers against evidence to prevent hallucinations.
    *   *Feature:* `⠋ Thinking...` Visual Feedback.
*   **Phase 10: Hierarchical Agency:** Split Goals (Long-Term vs Short-Term). Orma dynamically changes its immediate tactics (Zero-Latency) based on boredom or context tags (`[GOAL: ...]`).

---

## 🟡 THE NEXT FRONTIER (Road to Level 4)

### Level 4: The Expert Agent (Recursion & Expansion)
*The AI becomes a capable worker that can handle long-horizon tasks.*

#### Phase 11: Recursive Planning
*   **Concept:** Ability to break a vague goal ("Research the history of AI") into a 10-step plan and execute it autonomously over multiple turns.
*   **Tech:** Directed Acyclic Graph (DAG) for task management.

#### Phase 12: Code Autonomy (Self-Correction)
*   **Concept:** Orma gains the ability to write, run, and *fix* its own Python scripts in a sandboxed environment.
*   **Tech:** secure `exec()` sandbox, containerization (Docker).

#### Phase 13: Multi-Modal Perception
*   **Concept:** "Eyes and Ears". Giving Orma the ability to see images (Vision) and hear audio (STT).
*   **Tech:** Integrating `Gemini-Pro-Vision` and `Whisper`.

---

## 🔴 THE FINAL HORIZON (Road to Level 5)

### Level 5: Superintelligence (Novelty)
*The AI creates new knowledge.*

#### Phase 14: The Scientist
*   **Concept:** Hypothesis generation and testing. Orma runs experiments (code or search) to answer questions that have no Googleable answer.

#### Phase 15: Continuous Learning (The Soul Forge)
*   **Concept:** Fine-tuning its own weights/system prompts based on months of interaction. True conceptual evolution.
