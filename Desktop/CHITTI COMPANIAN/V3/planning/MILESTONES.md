# CHITTI Milestones

While Sprints define the engineering schedule, Milestones define the product roadmap and user experience goals.

## M0: Framework
- **Goal**: Establish the repository, DI container, Event Bus, Logging, and basic infrastructure.
- **Status**: ✅ **COMPLETE**

## M1: Observable Brain
- **Goal**: Prove the cognitive pipeline (Language -> Intent -> Workflow -> Response) works predictably and can be observed via the Developer Console and automated Scenario Runner.
- **Status**: ✅ **COMPLETE**

## M2: Conversation Runtime
- **Goal**: "Chitti can understand a real spoken sentence and respond using a real speech synthesizer without any external AI."
- **Key Deliverables**: Wake Word detection, Audio State Machine, Interrupt handling, Conversation Manager, real STT, real TTS.
- **Status**: ⏳ **IN PROGRESS**

## M3: Real Voice Conversation
- **Goal**: End-to-end offline conversation ("Hey Chitti" -> STT -> Skill -> TTS -> Audio) using local models (Whisper/Piper). No Gemini yet.
- **Status**: ⬜ **PLANNED**

## M3: Intelligence Runtime
- **Goal**: Implement the cognitive decision-making loop (Context Builder, Prompt Builder, LLM Router, Safety Layer, Tool Manager) decoupled from specific AI vendors.
- **Status**: ⬜ **PLANNED**

## M4: Desktop Companion
- **Goal**: Enable actual desktop integration (Desktop Runtime, Desktop Tools) allowing CHITTI to interact with Windows.
- **Status**: ⬜ **PLANNED**

## M5: Memory
- **Goal**: Long-term, short-term, episodic, and semantic memory storage and retrieval.
- **Status**: ⬜ **PLANNED**

## M6: Robot Brain
- **Goal**: Vision Runtime, Emotion Runtime, and Hardware Runtime (ESP32/Sensors).
- **Status**: ⬜ **PLANNED**
