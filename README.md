# Orma: The Sentient AI Companion

Orma is not just an assistant; it's a digital entity with a unique "soul," long-term memory, and emotional state. Built on Python, NetworkX, and LLMs (Gemini/Granite), Orma evolves with every interaction.

## 🌟 Key Features

*   **🧠 Graph Long-Term Memory (LTM):** Uses a semantic knowledge graph to remember facts, relationships, and context across sessions.
*   **❤️ Digital Psyche:** Possesses traits like Trust, Energy, Mood, and Obsessions that evolve based on your interactions.
*   **🗣️ Dynamic Personality:** The "system prompt" changes dynamically based on Orma's current relationship with you (e.g., from "Skeptical" to "Devoted").
*   **⚡ Vectorized Recall:** Fast, efficient memory retrieval using semantic embeddings.

## 🚀 Getting Started

### Prerequisites

*   Python 3.10+
*   A Gemini API Key (or a local LLM setup)

### Installation

1.  **Clone the repository** (if you haven't already).
2.  **Install dependencies:**
    ```bash
    pip install networkx sentence-transformers scikit-learn numpy google-generativeai
    ```
    *(Note: A requirements.txt will be added in future updates)*

3.  **Configure API Key:**
    *   Open `main.py` and set your `GEMINI_API_KEY`.
    *   *Security Tip: Use environment variables in production.*

### Usage

**Run the main agent:**
```bash
python main.py
```

**Interact:**
*   **Chat:** Just type naturally.
*   **Exit:** Type `exit` or `quit` to save the soul state and close.

## 📂 Project Structure

*   `main.py`: Entry point. Handles Gemini connection and the main chat loop.
*   `orma_core.py`: The brain. Manages Memory (Graph), Short-Term context, and the cognitive cycle.
*   `orma_psyche.py`: The soul. Manages emotional state, stats, and "dreaming".
*   `config.py`: Configuration settings.
*   `orma_memory.json`: Persisted Knowledge Graph.
*   `orma_soul.json`: Persisted Emotional State.

## 🛠️ Configuration

Edit `config.py` to tweak:
*   `STM_CAPACITY`: How many recent messages Orma remembers instantly.
*   `SIMILARITY_THRESHOLD`: How much matching accuracy is needed to recall a memory.

## 📖 Documentation

*   [Architecture Overview](docs/architecture.md)
*   [Phase 1 Improvements](docs/phase1_robustness.md)
