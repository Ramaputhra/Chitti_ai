import os

rule_text = """
## CHITTI AI Integration Constitution

### Rule 1 — Prefer Existing AI Models
Before implementing any AI-related feature, check whether the required capability is already covered by an approved model in Dependencies.txt.
If an approved model exists:
- Download it.
- Integrate it into CHITTI.
- Expose it through the AI Runtime.
- Reuse it everywhere.
Do not implement custom AI logic that duplicates an approved model's purpose.

### Rule 2 — Approved AI Stack
The following models are the official AI stack for CHITTI and must be treated as the default implementation unless there is a documented technical reason otherwise:
- Wake Word: openWakeWord
- Voice Activity Detection: Silero VAD
- Speech Recognition: Faster-Whisper
- Intent Classification: ModernBERT
- Entity Extraction: ModernBERT NER
- Capability Routing: ModernBERT
- Presentation Selection: ModernBERT
- Confidence & Tone: TinyBERT
- Memory Importance: TinyBERT
- Embeddings: BGE Small
- Semantic Search: BGE Small
- Search Ranking: BGE Reranker
- OCR: PaddleOCR
- Vision: SmolVLM-256M
- Planning & Conversation: Gemma 3 1B or Qwen2.5-1.5B
These models are the engineering baseline for CHITTI.

### Rule 3 — Never Reimplement AI
Do not write custom implementations for: Intent classification, Entity extraction, Semantic search, OCR, Wake word detection, Speech recognition, Tone detection, Confidence estimation, Presentation selection when an approved model already provides that functionality.

### Rule 4 — Write Integration, Not Replacement
AntiGravity is expected to write: Runtime code, Service layer, Model adapters, Provider wrappers, Download manager, Model manager, Caching, Scheduling, Hardware selection, Result normalization, Capability integration, Workflow orchestration.
AntiGravity is not expected to rewrite machine learning algorithms that already exist in approved models.

### Rule 5 — One Model, Many Features
Every model should be reused across the entire project. Never create multiple classifiers if one well-trained model can support all of them.

### Rule 6 — AI Runtime Owns Models
Capabilities must never import model libraries directly. The AI Runtime decides which model executes the request.
Forbidden: `from transformers import AutoModel`, `model.predict(...)`
Required: `intent = IntentService.classify(text)`

### Rule 7 — Document Exceptions
If AntiGravity decides not to use an approved model, it must explain: Why the model is unsuitable, Why a custom implementation is necessary, Why another approved model cannot solve the problem, The expected maintenance cost. Without this justification, the default assumption is that the approved model should be integrated rather than replaced.
"""

file_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\.agents\AGENTS.md"
with open(file_path, "a", encoding="utf-8") as f:
    f.write(rule_text)

print("Rules appended successfully.")
