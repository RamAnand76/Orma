# Phase 4: Episodic Memory

**Date:** December 2024
**Status:** Implemented

## Overview
Phase 4 introduces **Episodic Memory**—the ability to remember experiences chronologically, distinct from semantic facts. This gives Orma a continuous sense of self across sessions.

## Changes

### 1. `EpisodeMemory` Class
*   **Storage:** Saves summaries to `orma_episodes.json`.
*   **Structure:** `[{ "timestamp": 123456... , "summary": "We talked about X...", "date": "..." }]`.

### 2. Consolidation Process
*   **Trigger:** When the user types `exit`.
*   **Mechanism:** The current Short-Term Memory (STM) is sent to the LLM with a request to "Summarize this session in 3 sentences."
*   **Result:** The summary is appended to the episode list.

### 3. Recall
*   **Prompt Injection:** The summary of the **last episode** is now injected into the SYSTEM PROMPT every turn.
*   **Effect:** Orma knows what happened "Last time on Orma," allowing for continuity (e.g., "Welcome back! Last time we were discussing your project.").

## Usage
No new commands needed. Just chat and `exit` normally. Orma handles the rest.
