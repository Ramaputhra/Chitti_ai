# CHITTI V2 — VOICE PROVIDER GUIDE

Welcome to the **CHITTI V2 Voice Provider Integration Guide**. This guide explains how to add new TTS providers, map provider capabilities, and generate canonical `SpeechTimeline` objects.

---

## 1. How to Add a New TTS Provider
1. Create a provider class implementing the `synthesize(text, voice_profile, output_dir, speech_id)` contract.
2. Register the provider in `TTSManager` (`desktop/voice/runtime/tts_manager.py`).

---

## 2. Provider Abstraction Requirements
- Providers receive normalized text and return synthesized WAV audio file path + audio duration.
- Providers MUST NOT build custom prompt templates or manipulate cognitive state.

---

## 3. Generating SpeechTimeline
`SpeechTimelineBuilder` converts audio synthesis outputs and `SpeechMarkupMetadata` into a canonical `SpeechTimeline`:
```python
timeline = builder.build_timeline(
    speech_id=speech_id,
    audio_id=audio_id,
    duration=duration,
    language=language,
    voice_profile=voice_profile,
    style=style,
    markup=markup,
    provider="SherpaONNX",
    audio_path=audio_path
)
```
