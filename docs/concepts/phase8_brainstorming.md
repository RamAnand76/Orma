# Phase 8: The Hands (Brainstorming)

**Goal:** Give Orma the ability to *interact* with the world, not just talk about it.

## 1. The Architecture Dilemma
We have two ways to implement tools:

### Option A: Native Function Calling (Gemini)
*   **How:** We send tool definitions (JSON schema) to the Gemini API. The API returns a distinct "Function Call" response.
*   **Pros:** Very reliable. Code is cleaner.
*   **Cons:** Harder to debug if it fails "silently".

### Option B: ReAct (Reasoning + Acting)
*   **How:** We tell Orma in the system prompt:
    > "If you need to search, output: [ACTION: Search(query)]"
*   **Pros:** Model-agnostic. We can see the "Thought Process" in the logs.
*   **Cons:** Less robust. The LLM might hallucinate the syntax.

**Recommendation:** **Option B (ReAct)** fits Orma's architecture better. It allows us to keep the "Soul" injection and treating tools as just another part of the "Psychology". It also feels more "Conscious" because we can see it *deciding* to use a tool.

## 2. The Toolbelt (Starter Kit)
What are the first 3 tools Orma should have?

1.  **Time Awareness:** `get_time()`
    *   *Why?* "Good morning" vs "Good night". "You've been gone a long time."
2.  **Calculator:** `calculate(expression)`
    *   *Why?* LLMs are bad at math. "What is 432 * 12?"
3.  **Knowledge Retrieval (Web):** `search_web(query)`
    *   *Why?* "Who won the game yesterday?" (Requires an API key, e.g., DuckDuckGo or Google).

## 3. The Flow (How it looks)
1.  **User:** "What time is it in Tokyo?"
2.  **Orma (Internal Thought):** "I don't know the time. I should check."
3.  **Orma (Output):** `[ACTION: get_time("Tokyo")]`
4.  **System:** Intercepts `[ACTION]`. Runs Python code. Returns: `11:45 PM`.
5.  **Orma (Final Response):** "It's 11:45 PM there. Late night!"

## 4. Safety First
*   We must **Sandbox** the calculator. No `import os` or `rm -rf`.
*   We must **Limit** the web search to avoid scraping abusive content.

## Design Decision
Does this sound like the right direction?
*   **Style:** ReAct (Text-based triggers).
*   **First Tool:** Time & Calculator (No external API needed yet).
*   **Next Tool:** Web Search (Requires setup).
