# Phase 2: Reliability Fixes

**Date:** December 2024
**Status:** Implemented

## Overview
Phase 2 addressed a critical bug where the memory extraction system would fail to learn new facts because the LLM returned JSON in an unexpected format (often a list of lists instead of a list of objects).

## Changes

### Robust Parsing in `_memorize`
We updated `orma_core.py` to handle multiple JSON formats dynamically.

**Supported Formats:**
1.  **Standard:** `[{"source": "A", "relation": "B", "target": "C"}]`
2.  **Fallback:** `[["A", "B", "C"]]`

### Prompt Engineering
The prompt sent to the LLM during the memorization step was tightened:
*   Explicitly requests a **JSON LIST of objects**.
*   Added instructions to clean Markdown code blocks (e.g., ` ```json ... ``` `) which often break simple parsers.

### Debugging
*   If parsing fails, the system now logs the **Raw Output** from the LLM. This allows developers to see exactly what the model said that caused the crash.
