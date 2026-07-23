# CHITTI Desktop Companion Blueprint (Version 1.0)

This document defines **What CHITTI is.** It is the foundational vision for the project.

## 1. What CHITTI Is
CHITTI is a local-first, privacy-respecting, extensible Desktop AI Companion designed for Windows. It acts as an intelligent assistant that lives on the user's desktop, observing, remembering, and assisting with daily productivity without requiring constant manual invocation.

## 2. Core Pillars
1. **Local-First AI Execution**: Support for local LLMs (Ollama, LM Studio) as the primary intelligence engine to ensure privacy and low latency.
2. **Local Voice Pipeline**: Offline Wake Word detection, continuous Speech-to-Text (Whisper), and Text-to-Speech (Piper) for natural hands-free interaction.
3. **Companion Presence**: A minimal system tray icon and visual overlay widget indicating states (Listening, Thinking, Speaking, Working) so the user always knows what CHITTI is doing.
4. **Desktop Intelligence**: Ability to launch applications, manipulate files, extract document text, and automate basic OS tasks safely.
5. **Personal & Productivity Intelligence**: Automatic tracking of active windows, process lifecycles, and work sessions to determine the user's semantic intent and build episodic memory.

## 3. What CHITTI Is Not
CHITTI is not a cloud service, not an abstract research framework, and not an autonomous web scraper. It does not replace the user; it works alongside them.

## 4. Architectural Philosophy
*   **Layered Intelligence**: Intelligence emerges from layered deterministic systems (Observations -> Activities -> Intent -> Planning).
*   **Isolated Runtimes**: Every runtime has a single responsibility. No runtime may bypass the Event Bus to communicate with another.
*   **The Planner Decides**: Runtimes only report facts. The Planner is the exclusive decision-maker for actions.

Everything outside this definition (Robotics, Cloud Sync, Mobile App) is considered Post-MVP and is strictly excluded from current development.
