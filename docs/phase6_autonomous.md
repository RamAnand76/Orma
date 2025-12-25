# Phase 6: The Autonomous Loop

**Date:** December 2024
**Status:** Implemented

## Overview
Phase 6 is a paradigm shift. It transforms Orma from a **Reactive Tool** (Speak when spoken to) into an **Autonomous Companion** (Can speak first).

## Architecture Changes

### 1. Multi-Threaded Core (`main.py`)
*   **Thread A (Input Ear):** A dedicated thread that waits for `input()`. This ensures the terminal doesn't "freeze" the whole program while waiting for you to type.
*   **Thread B (The Brain):** The main loop runs continuously (Heartbeat).
    *   It checks for messages from Thread A.
    *   If no messages, it increments a "Silence Timer".

### 2. The Subconscious (`ponder`)
*   **Mechanism:** Added `ponder()` to `orma_core.py`.
*   **Trigger:** When `Silence Timer > BOREDOM_THRESHOLD` (Configured in `config.py`, default 60s).
*   **Action:** Orma rolls a die (`ACTION_PROBABILITY`). If successful, it generates a message based on its **Current Goal**.

## Usage
*   **Start:** `python main.py`
*   **Interaction:** You can chat normally.
*   **The Magic:** If you stop typing and wait 60 seconds, Orma will get "bored" and text you proactively.
*   **Exit:** Type `exit` to save and quit.

## Configuration
Adjust these in `config.py`:
*   `BOREDOM_THRESHOLD`: Seconds before thinking starts.
*   `ACTION_PROBABILITY`: Chance of acting when bored (0.0 - 1.0).
