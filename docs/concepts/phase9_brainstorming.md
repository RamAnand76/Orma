# Phase 9: The Mirror (Brainstorming)

**Goal:** Give Orma the ability to "think about its thoughts" (Metacognition) before speaking. This moves it from *Reactive Tool User* to *Reflective Agent*.

## The Problem
Currently, Orma is "Impulsive."
1.  **Input:** "Who won the Kerala League?"
2.  **Tool:** Returns valid data ("Kannur won").
3.  **Process:** Internal bias (or confusion) overrides data.
4.  **Output:** "Thiruvananthapuram won!" (Hallucination).

Orma speaks the *first thing* that comes to its "mind" (the LLM generation). It lacks an internal filter to say, "Wait, that contradicts the tool result."

## The Solution: The Mirror
We need to insert a **Self-Reflection Step** between *Thinking* and *Speaking*.

### Option A: The "Thought Chain" (Prompt Engineering)
Change the system prompt to force a "Thought" block before the "Response".
```
[THOUGHT]
The user asked about the Kerala League.
My tool result says "Kannur Warriors".
My internal training data is old/conflicting.
I must trust the tool.
[DECISION] Answer "Kannur Warriors".

[RESPONSE]
Kannur Warriors won!
```
*   **Pros:** Simple, fast (one LLM call).
*   **Cons:** LLMs often ignore instructions to be self-critical in the same generation.

### Option B: The "Critic Loop" (Two-Pass Architecture)
1.  **Draft:** Orma generates a draft response.
2.  **Critique:** A separate prompts asks: "Context says X. Draft says Y. Is this accurate?"
3.  **Refine:** If conflicting, regenerate.
*   **Pros:** Highly robust. Catches 90% of hallucinations.
*   **Cons:** Slower (2x LLM calls), more expensive.

### Option C: The "Inner Monologue" (Stream of Consciousness)
Inject a dynamic "Inner Monologue" into the chat history *as if* it were a system message, but visible only to the AI.
- `orma -> inner_voice`: "This snippet is confusing. It says 'prevail over', does that mean 'won'? Let me check the next result..."
*   **Pros:** Feels very human/AGI.
*   **Cons:** Complex to implement statefully.

## Recommended Approach: Hybrid (Thought Chain)
For Phase 9, we start with **Option A (Thought Chain)** but structured strictly in the code.
1.  We force the LLM to output a JSON or strict XML block `[REFLECTION] ... [/REFLECTION]` before the answer.
2.  The `OrmaEngine` parses this.
3.  If the reflection indicates low confidence, we can trigger a re-search or a disclaimer.

## Implementation Steps
1.  **Refactor Prompt:** Update `POWER PROMPT` to demand a `[thought]` block.
2.  **Hide Thoughts:** Ensure the user *only* sees the final answer, but the logs show the thinking.
3.  **Self-Correction:** If the thought says "I need to check again", trigger a tool loop *automatically* (this touches on Phase 6 Autonomous Loop concept).
