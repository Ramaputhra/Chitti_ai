# Implemented Features

This document inventories every capability currently fully implemented and functional within the repository.

### Audio Pipeline
* **Status**: Complete
* **Completion**: 100%
* **Dependencies**: None
* **Test Status**: Passed
* **MVP Ready**: Yes
* **Notes**: Handles microphone input, speaker output, and Voice Activity Detection (VAD).

### Speech-to-Text (STT)
* **Status**: Complete
* **Completion**: 100%
* **Dependencies**: Audio Pipeline
* **Test Status**: Passed
* **MVP Ready**: Yes
* **Notes**: Uses local Whisper model (`whisper_provider.py`) for offline transcription.

### Text-to-Speech (TTS)
* **Status**: Complete
* **Completion**: 100%
* **Dependencies**: Audio Pipeline
* **Test Status**: Passed
* **MVP Ready**: Yes
* **Notes**: Uses local Piper model (`piper_provider.py`) for high-speed offline speech synthesis.

### Core Event Bus
* **Status**: Complete
* **Completion**: 100%
* **Dependencies**: None
* **Test Status**: Passed
* **MVP Ready**: Yes
* **Notes**: Thread-safe synchronous routing for Events, Commands, Requests, and Responses.

### AI Routing & Prompt Builder
* **Status**: Complete
* **Completion**: 90%
* **Dependencies**: None
* **Test Status**: Passed
* **MVP Ready**: Yes
* **Notes**: Deterministic context budgeting and telemetry. Connects to Ollama and OpenAI fallback.
