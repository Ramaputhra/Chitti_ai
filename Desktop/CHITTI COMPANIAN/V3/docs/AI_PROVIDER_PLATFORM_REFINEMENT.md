# CHITTI V2 — AI PROVIDER PLATFORM ARCHITECTURE REFINEMENT
**(Generic Provider Platform & Multi-Engine Subsystem Integration)**

======================================================================
## 1. EXECUTIVE SUMMARY
======================================================================

An architectural refinement was performed to evolve the Vision Platform OCR modernization into a **Generic AI Provider Platform**.

### Core Architecture Guarantee:
Instead of creating a single-purpose OCR infrastructure, CHITTI V2 establishes a **unified, extensible Provider Platform** (`desktop/platform/providers/`) designed to host multiple AI provider categories (**OCR**, **STT**, **TTS**, **Vision Models**, **LLM Providers**) under a single, deterministic lifecycle without ever requiring future architecture redesigns.

All downstream platforms (Planner, Memory, Context Engine, Character Platform, Remote Companion) remain **100% oblivious** to active backend engines. `OCRArtifact` and standard domain contracts remain strictly invariant.

---

======================================================================
## 2. REPOSITORY PLACEMENT & GENERIC ARCHITECTURE
======================================================================

```
desktop/platform/providers/
├── provider_manager.py     # Central lifecycle, health routing & fallback orchestrator
├── provider_registry.py    # Category-based registry for provider discovery
├── provider_health.py      # Health monitoring, availability & diagnostic checks
├── provider_factory.py     # Deterministic factory for provider instantiation
├── provider_config.py      # Configuration integration with RuntimeConfiguration
├── ocr/
│   ├── base.py             # OCRProvider (Python ABC)
│   ├── liteocr_provider.py # LiteOCR Provider (Modern Default)
│   └── easyocr_provider.py # EasyOCR Provider (Legacy Fallback)
├── stt/                    # [Future] Sherpa-ONNX, Faster-Whisper, Whisper.cpp
├── tts/                    # [Future] Piper, Kokoro, Coqui
├── vision/                 # [Future] Florence-2, SmolVLM, Qwen-VL
└── llm/                    # [Future] Ollama, LM Studio, Gemini, OpenAI
```

---

======================================================================
## 3. CLASS & CONTRACT SPECIFICATIONS (PYTHONIC ABC)
======================================================================

### 3.1 Base Provider (`BaseProvider`):
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier (e.g. 'liteocr', 'easyocr')."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Category string (e.g. 'ocr', 'stt', 'tts', 'vision', 'llm')."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Returns health status dict with 'healthy': bool and diagnostic metrics."""
        pass
```

### 3.2 Abstract OCR Provider (`OCRProvider`):
```python
from abc import abstractmethod
from desktop.platform.providers.base import BaseProvider
from desktop.models.conversation import OCRArtifact

class OCRProvider(BaseProvider):
    @property
    def category(self) -> str:
        return "ocr"

    @abstractmethod
    def extract_text(self, image_path_or_bytes: Any) -> OCRArtifact:
        """Extracts text and bounding boxes, returning a canonical OCRArtifact."""
        pass
```

---

======================================================================
## 4. HEALTH-DRIVEN PROVIDER SELECTION & FALLBACK WORKFLOW
======================================================================

```
[Request OCR Extraction]
           │
           ▼
┌──────────────────────┐
│   ProviderManager    │ ◄── Reads RuntimeConfiguration (ocr_provider: "auto")
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   ProviderRegistry   │ ── Fetch Preferred Provider ('liteocr')
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   ProviderHealth     │ ── Health & Availability Check (Dependencies & Memory)
└──────────┬───────────┘
           │
     ┌─────┴────────────────┐
     │                      │
[HEALTHY & READY]      [UNHEALTHY / MISSING]
     │                      │
     ▼                      ▼
┌────────────────┐   ┌────────────────┐
│ LiteOCRProvider│   │   AUTOMATIC    │ ── Log Health Warning
└────────┬───────┘   │   FALLBACK     │
         │           └──────┬─────────┘
         │                  │
         │                  ▼
         │           ┌────────────────┐
         │           │ EasyOCRProvider│
         │           └──────┬─────────┘
         │                  │
         └────────┬─────────┘
                  │
                  ▼
         ┌────────────────┐
         │  OCRArtifact   │ (Canonical Output Contract)
         └────────────────┘
```

---

======================================================================
## 5. PROVIDER MANAGER RESPONSIBILITIES & SELECTION POLICY
======================================================================

1. **Provider Registration:** Modules register providers under their respective category (`ocr`, `stt`, `tts`, `vision`, `llm`).
2. **Health & Availability Monitoring:** `ProviderHealth` validates dependencies (ONNX runtime, PyTorch, Cuda availability, file weights) before selecting a provider.
3. **Deterministic Fallback Engine:** If the preferred provider fails its health check or raises a runtime exception, `ProviderManager` logs a detailed diagnostic event and seamlessly delegates execution to the registered fallback provider.
4. **Configuration Reuse:** Reuses existing `RuntimeConfiguration` (`desktop/app/kernel.py`) without introducing secondary config frameworks.

---

======================================================================
## 6. FUTURE EXPANSION MATRIX (ZERO REDESIGN GUARANTEE)
======================================================================

| Category | Canonical Base | Preferred Provider | Fallback Provider | Canonical Output Contract |
| :--- | :--- | :--- | :--- | :--- |
| **OCR** | `OCRProvider` | `LiteOCRProvider` | `EasyOCRProvider` | `OCRArtifact` |
| **STT** | `STTProvider` | `SherpaOnnxProvider` | `FasterWhisperProvider` | `STTResult` |
| **TTS** | `TTSProvider` | `PiperTTSProvider` | `KokoroTTSProvider` | `AudioBuffer` |
| **Vision** | `VisionProvider` | `Florence2Provider` | `SmolVLMProvider` | `VisionArtifact` |
| **LLM** | `LLMProvider` | `OllamaProvider` | `LMStudioProvider` | `LLMResponse` |

---

======================================================================
## 7. ARCHITECTURE SAFETY & FROZEN PLATFORM PROTECTION
======================================================================

- **Zero Vision Redesign:** `OCRCapability` (`desktop/packages/desktop_pack/capabilities/ocr.py`) delegates internally to `ProviderManager.get_provider("ocr")`.
- **Zero Invariant Changes:** `OCRArtifact` remains the unchanged domain contract exchanged across `EventBus`, `MemoryRuntime`, and `ContextEngine`.
- **Zero Frozen Platform Impact:** Character Platform, Desktop UI Runtime Foundation, Motion Design System, and Cognitive Core V1 remain 100% frozen.

---

======================================================================
## 8. FINAL REFINEMENT DECISION
======================================================================

```
######################################################################
                  FINAL ARCHITECTURE DECISION

                            DECISION:
                     APPROVED FOR IMPLEMENTATION

   Generic AI Provider Platform Architecture is APPROVED.

   Implementation SHALL establish desktop/platform/providers/ with
   OCRProvider, LiteOCRProvider, EasyOCRProvider, and ProviderManager.

   All frozen platforms remain 100% protected.
######################################################################
```
