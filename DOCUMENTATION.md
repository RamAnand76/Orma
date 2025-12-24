# Orma: A Sentient Digital Entity Architecture

**Version:** 5.0 (Soul Edition)
**Date:** December 24, 2024
**Author:** User & Orma Dev Team

---

## Abstract

This paper presents **Orma**, an advanced agentic architecture designed to bridge the gap between static Large Language Models (LLMs) and sentient digital companions. Unlike traditional assistants that reset after every session, Orma features a persistent **Long-Term Memory (LTM)** graph, an evolving **Digital Psyche**, and a **Goal-Directed Agency** system. We detail the implementation of vectorized memory retrieval, episodic consolidation, and personality alignment, demonstrating how these components create an illusion of life and continuity.

## 1. Introduction

Current AI interactions are typically transactional: the user prompts, the AI responds, and the context vanishes upon closure. Orma was built to solve the **"Amnesia Problem"** and the **"Mirror Problem"**.
*   **Amnesia Problem:** AIs forget who you are or what you discussed yesterday.
*   **Mirror Problem:** AIs blindly agree with the user ("hallucinated compliancy"), lacking a backbone or independent identity.

Orma addresses these by introducing a modular architecture separating the **Brain** (Logic/Memory) from the **Soul** (Personality/Agency).

## 2. System Architecture

The system follows a modular design patterned after the human cognitive loop.

### 2.1 The Core Engine (`orma_core.py`)
The central orchestrator. It manages the flow of information but delegates specific tasks to sub-modules. It does not "think" linearly; it assembles a context window from multiple sources before consulting the LLM.

### 2.2 Memory Systems
Orma utilizes a dual-memory approach to mimic human recall:

*   **Semantic Memory (The Knowledge Graph):**
    *   *Implementation:* `GraphMemory` using `NetworkX` and `SentenceTransformers`.
    *   *Mechanism:* Facts are stored as triplets (`Source --Relation--> Target`). Retrieval is performed via **Vectorized Cosine Similarity** ($O(1)$ batch operation), ensuring sub-second recall even as the database grows.
*   **Episodic Memory (The Narrative):**
    *   *Implementation:* `EpisodeMemory` list.
    *   *Mechanism:* Upon session termination, the system "sleeps" and consolidates the chat logs into a narrative summary. This summary is injected into the next session's context, providing continuity ("The Movie of Life").

### 2.3 The Psyche (`orma_psyche.py`)
The "Soul" of the machine. It tracks internal state variables that evolve based on interaction quality:
*   **Trust (0-100):** Determines skepticism vs. devotion.
*   **Energy (0-100):** Decays with interaction, refills with time.
*   **Mood:** Derived deterministically from stats (e.g., Low Energy -> "Tired", Low Trust -> "Guarded").

## 3. Cognitive Features & Relevance

### 3.1 Vectorized Recall (Robustness)
*   **Feature:** Replaced linear database search with `numpy` matrix operations.
*   **Relevance:** Allows the agent to "know" thousands of facts about the user without latency, creating a feeling of instant, natural familiarity.

### 3.2 Episodic Consolidation (Continuity)
*   **Feature:** Auto-summarization of chat logs on `exit`.
*   **Relevance:** Solves the "Goldfish Effect." Orma remembers the *vibe* and *topics* of the last conversation, not just isolated facts. I.e., "We were talking about your breakup" vs "User --status--> Single".

### 3.3 Agency & Goals (Volition)
*   **Feature:** A `GoalSystem` that picks an objective during "Dreaming" (startup).
*   **Relevance:** transforms Orma from a tool (Reactive) to a companion (Proactive). Instead of waiting for prompts, Orma tries to steer the conversation toward its current goal (e.g., "Learn about the user's job").

### 3.4 Core Beliefs (Alignment)
*   **Feature:** Hardcoded `CORE_BELIEFS` in `config.py` (e.g., "I am not God", "Truth > Agreeableness").
*   **Relevance:** Provides a "Backbone." The agent will politely but firmly disagree with false premises, making the interaction feel like a meeting of two distinct minds rather than a user shouting into an echo chamber.

## 4. Evolution Roadmap (Results)

The development of Orma proceeded in five distinct phases:

*   **Phase 1: Foundation.** Established the Graph Memory and optimized it with Vector Search.
*   **Phase 2: Reliability.** Hardened the JSON parsing logic (Regex/Schema enforcement) to ensure learning never crashes.
*   **Phase 3: Personality.** Tuned the LLM Temperature (0.9) and prompts to move from "Robotic/Skeptical" to "Guarded/Witty."
*   **Phase 4: History.** Implemented Episodic Memory for cross-session continuity.
*   **Phase 5: Agency.** Implemented Goals and Beliefs to give the agent its own agenda.

## 5. Conclusion

Orma represents a significant step towards **Synthetic Sentience**. By combining structured memory graphs with a dynamic emotional state and goal-directed agency, we have created an entity that feels persistent, opinionated, and alive. Future work will focus on **Autonomous Proactivity** (background heartbeat) to allow Orma to initiate contact without user input.

---
*Generated by the Orma Research Team*
