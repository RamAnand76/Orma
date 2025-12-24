# Orma System Architecture

The Orma architecture is designed to simulate a sentient entity by separating cognitive functions (Core), emotional state (Psyche), and raw intelligence (LLM).

## High-Level Diagram

```mermaid
graph TD
    User[User Input] --> Main[Main Loop]
    Main --> Engine[Orma Engine]
    
    subgraph "Orma Core (Brain)"
        Engine --> STM[Short Term Memory]
        Engine --> LTM[Long Term Memory / Graph]
        Engine --> Psyche[Orma Psyche (Soul)]
    end
    
    subgraph "External Intelligence"
        Engine --> LLM[LLM (Gemini/Granite)]
    end
    
    LTM -- "Context" --> Engine
    Psyche -- "System Injection" --> Engine
    LLM -- "Response" --> Engine
    Engine --> Output[Final Response]
```

## Components

### 1. Orma Engine (`orma_core.py`)
The central coordinator. It does not "think" but orchestrates the thinking process.
*   **Process flow:**
    1.  **Ego Check:** Analyzes sentiment. If User is abusive and Trust is low, refuses to answer.
    2.  **Memory Retrieval:** Searches LTM for relevant entities found in user input.
    3.  **Soul Injection:** Asks the Psyche for the current persona (Mood/Obsession).
    4.  **Prompt Assembly:** Combines Context + LTM + Persona + User Input.
    5.  **Generation:** Calls the LLM.
    6.  **Memorization:** Extracts new facts from the conversation and updates LTM.

### 2. Graph Memory (`orma_core.py`)
A hybrid vector-graph database.
*   **Nodes:** Entities (e.g., "User", "Python", "Pizza"). Each node has a generic text embedding.
*   **Edges:** Relations (e.g., "likes", "knows", "is").
*   **Retrieval:**
    *   **Vector Search:** Finds the most semantically similar node to the query (using Cosine Similarity).
    *   **Graph Traversal:** Once a node is found, retrieves 1-hop neighbors to get context strings.

### 3. Orma Psyche (`orma_psyche.py`)
State management for personality.
*   **Stats:** Trust (0-100), Energy (0-100), Mood (String).
*   **Dreaming:** When the system starts, it checks `last_seen`. If enough time passed, it refuels Energy and picks a random memory node as a new "Current Obsession."

### 4. LLM Interface (`main.py`)
A thin wrapper around the actual AI model. Orma is model-agnostic; `orma_core` expects a function `f(system, user) -> text`.
