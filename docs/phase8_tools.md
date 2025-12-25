# Phase 8: The Hands (Tool Use)

This phase evolved Orma from a text-based conversationalist to an **Agent** capable of interacting with the external world (AGI Level 3).

## 1. Tool Architecture
The system uses a **ReAct (Reasoning + Acting)** pattern, where the LLM decides to use a tool by outputting a specific action tag, rather than using native function calling APIs (which closes the "black box" of thought).

### The Tool Registry (`tools/registry.py`)
A central registry that loads available tools. It is pluggable, allowing new tools to be added easily.

```python
# Usage in orma_core.py
self.tools = ToolRegistry()
result = self.tools.execute("tool_name", "arguments")
```

### The Base Tool (`tools/base.py`)
All tools inherit from `BaseTool`, enforcing a standard interface:
- `name`: Unique identifier (e.g., `search_web`).
- `description`: Instructions for the LLM on when to use it.
- `execute(args)`: The logic.

## 2. Implemented Tools

### A. Web Search (`tools/search/ddgs_tool.py`)
**Library:** `ddgs` (DuckDuckGo Search) - *Free, Open Source, Real-time.*
- **Trigger:** When user asks about current events, news, or facts post-2023.
- **Mechanism:** Searches specifically for the query and retrieves titles, snippets, and URLs.
- **Handling:** The System Prompt instructs Orma to trust the [TOOL RESULT] over its internal memory if conflicts arise.

### B. Time (`tools/utils/basic.py`)
- **Name:** `get_time`
- **Function:** Returns current local system time.
- **Use Case:** "What time is it?", "What is the date?"

### C. Calculator (`tools/utils/basic.py`)
- **Name:** `calculate`
- **Function:** Safe mathematical evaluation using Python's `ast` module (avoids unsafe `eval`).
- **Use Case:** "What is 123 * 456?"

## 3. Cognitive Integration
In `orma_core.py`, the `_execute_tool_if_needed` method acts as the "Hands":
1.  **Detect:** Scans LLM output for `[ACTION: tool_name(args)]`.
2.  **Execute:** calls the tool.
3.  **Inject:** Feeds the result back into the LLM context.
4.  **Synthesize:** The LLM generates the final natural language response based on the result.

## 4. Robustness
- **Argument Parsing:** Robust regex handles `key=value` or quoted arguments.
- **Context Injection:** Follow-up prompts remind the LLM of the original user question to prevent context loss.
- **Error Handling:** Empty memory files or tool errors are caught and logged without crashing the main loop.
