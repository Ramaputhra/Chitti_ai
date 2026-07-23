# CHITTI COMPANIAN: MVP Experiences

This document replaces traditional feature roadmaps. CHITTI's progress is measured exclusively by end-to-end experiences that a non-technical person can demonstrate in under one minute. 

**Rule: An experience is not complete until the entire pipeline (Listen -> Understand -> Act -> Respond) executes flawlessly.**

---

## Experience 001: The Speech Pipeline MVP
**User Says:** *"Chitti, open Downloads."*

**Success Criteria:**
- **Listen:** Wake Word (openWakeWord) detects "Chitti". VAD (Silero) crops the silence. Faster-Whisper transcribes "Open Downloads".
- **Understand:** Semantic Runtime extracts the intent (System/FolderOpen) and entity (Downloads).
- **Act:** Execution Engine opens the Windows Downloads folder.
- **Respond:** Piper TTS synthesizes and plays *"Opening your Downloads folder."*
- **Bonus:** Experience Engine observes the success silently (no behavior change yet).

---

## Experience 002: Capability Library Staging
**User Says:** *"Chitti, open my folder,"* followed by subsequent copy, move, rename, and delete commands.

**Success Criteria:**
- **Incremental Staging:** Capabilities are built incrementally across Phase A (Reference), Phase B (Safe Write), and Phase C (Dangerous).
- **Test Scenarios:** Every capability passes three scenarios:
  1. **Happy Path:** Pipeline succeeds seamlessly.
  2. **Recoverable Failure:** Planner handles transient failures (e.g., path resolving) and recovers.
  3. **Permanent Failure:** Execution gracefully terminates and reports failure to the user without crashing.
- **Pipeline Validation:** The test must validate the full experience (Listen -> Understand -> Act -> Respond), not just adapter execution.

---

## Experience 003: Memory & Semantic Retrieval
**User Says:** *"Chitti, where did I save my screenplay?"*

**Success Criteria:**
- **Understand:** Recognizes a semantic query rather than a direct path.
- **Act:** Embeds the query via `multilingual-e5-small`. Retrieves the file path from local SQLite/Vector storage.
- **Respond:** Piper TTS synthesizes *"I found it in your Documents under 'Writing Projects'."*

---

## Experience 004: Visual Desktop Reasoning
**User Says:** *"Chitti, what is on my screen?"*

**Success Criteria:**
- **Act:** Triggers an automatic desktop screenshot. PaddleOCR and SmolVLM process the image. 
- **Respond:** TTS responds with a contextual summary (e.g., *"You are looking at a code editor with the CHITTI project open, and a web browser on the right."*)

---

## Experience 005: Multi-Step Execution
**User Says:** *"Chitti, copy these files into a new folder named 'Archive'."*

**Success Criteria:**
- **Listen/Understand:** Extracts multi-step entities (Selection context, Create Folder, Move/Copy).
- **Act:** Reads current OS selection context. Creates directory. Moves files.
- **Respond:** TTS synthesizes *"Archived 5 files successfully."*
