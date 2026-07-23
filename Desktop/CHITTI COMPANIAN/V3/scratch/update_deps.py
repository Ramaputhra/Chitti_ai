import os

path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\Project Goals\Dependencies.txt"

content = """Below is the stack I would recommend **specifically for CHITTI**. The goal is to cover all of CHITTI's capabilities with the fewest, smallest, and most reusable models.

| CHITTI Function                    | Provider                  | Default Model                             |              Approx. Size |
| ---------------------------------- | ------------------------- | ----------------------------------------- | ------------------------: |
| Wake Word                          | Wake Word Provider        | openWakeWord                              |               **5–15 MB** |
| Voice Activity Detection           | VAD Provider              | Silero VAD                                |                  **2 MB** |
| Speech-to-Text                     | Speech Provider           | Faster-Whisper Tiny                       |                 **39 MB** |
| Speech-to-Text (Better Accuracy)   | Speech Provider           | Faster-Whisper Base                       |                 **74 MB** |
| Intent Classification              | Intent Provider           | XLM-RoBERTa                               |               **500 MB**  |
| Tool Selection                     | Capability Routing        | XLM-RoBERTa                               |               **500 MB**  |
| Parameter Extraction               | Entity Provider           | XLM-RoBERTa (NER fine-tuned)              |               **500 MB**  |
| Follow-up Decision                 | Decision Provider         | TinyBERT                                  |              **20–50 MB** |
| Conversation Tone                  | Tone Provider             | TinyBERT                                  |              **20–50 MB** |
| Humor Selection                    | Humor Provider            | TinyBERT                                  |              **20–50 MB** |
| Notification Priority              | Priority Provider         | TinyBERT                                  |              **20–50 MB** |
| Memory Importance                  | Importance Provider       | TinyBERT                                  |              **20–50 MB** |
| Confidence Estimation              | Confidence Provider       | TinyBERT                                  |              **20–50 MB** |
| Presentation Selector              | Presentation Provider     | XLM-RoBERTa                               |               **500 MB**  |
| HTML Template Selector             | Template Provider         | XLM-RoBERTa                               |               **500 MB**  |
| Workspace Classifier               | Workspace Provider        | XLM-RoBERTa                               |               **500 MB**  |
| Project Classifier                 | Project Provider          | XLM-RoBERTa                               |               **500 MB**  |
| Reminder Classifier                | Reminder Provider         | XLM-RoBERTa                               |               **500 MB**  |
| Semantic Search                    | Embedding Provider        | BGE-M3                                    |              **2.2 GB**   |
| Memory Retrieval                   | Embedding Provider        | BGE-M3                                    |              **2.2 GB**   |
| File Search                        | Embedding Provider        | BGE-M3                                    |              **2.2 GB**   |
| Knowledge Retrieval                | Embedding Provider        | BGE-M3                                    |              **2.2 GB**   |
| Search Result Ranking              | Reranker Provider         | BGE-Reranker-v2-m3                        |              **2.2 GB**   |
| OCR                                | OCR Provider              | PaddleOCR                                 |              **20–30 MB** |
| Screen Understanding               | Vision Provider           | SmolVLM-256M                              |                **256 MB** |
| Image Understanding                | Vision Provider           | SmolVLM-256M                              |                **256 MB** |
| Visual Verification                | Vision Provider           | SmolVLM-256M                              |                **256 MB** |
| UI Element Recognition             | Vision Provider           | SmolVLM-256M                              |                **256 MB** |
| General Conversation               | Reasoning Provider        | Gemma 3 1B                                |    **700–900 MB (4-bit)** |
| General Conversation (Alternative) | Reasoning Provider        | Qwen2.5-1.5B                              | **900 MB–1.2 GB (4-bit)** |
| Planning                           | Reasoning Provider        | Qwen2.5-1.5B                              | **900 MB–1.2 GB (4-bit)** |
| Context Building                   | Embedding Provider        | Qwen2.5-1.5B + BGE-M3                     |          **Reuse models** |
| Web Summarization                  | Reasoning Provider        | Gemma 3 1B / Qwen2.5-1.5B                 |           **Reuse model** |
| Learning New Intents               | Reasoning Provider        | Gemma 3 1B / Qwen2.5-1.5B                 |           **Reuse model** |
| Local Intent Evolution             | Experience Learning Engine| SQLite + Intent Library                   |           **No AI model** |

---

# Models Reused Across Multiple CHITTI Features

| Model                         | Covers                                                                                          |
| ----------------------------- | ----------------------------------------------------------------------------------------------- |
| **openWakeWord**              | Wake word detection                                                                             |
| **Silero VAD**                | Speech detection                                                                                |
| **Faster-Whisper**            | All speech recognition                                                                          |
| **XLM-RoBERTa**               | Intent, routing, entity extraction (NER), presentation selection, reminders, workspace classification |
| **TinyBERT**                  | Confidence, tone, humor, priorities, follow-up decisions                                        |
| **BGE-M3**                    | Semantic search, memories, files, projects, knowledge (Multilingual)                            |
| **BGE-Reranker-v2-m3**        | Better search accuracy (Multilingual)                                                           |
| **PaddleOCR**                 | OCR                                                                                             |
| **SmolVLM-256M**              | Vision, UI understanding, visual verification                                                   |
| **Gemma 3 1B / Qwen2.5-1.5B** | Reasoning, planning, unknown requests, conversation                                             |

---

# Models You Should Eventually Train for CHITTI

| Future CHITTI Model | Base Model    | Purpose                       | Estimated Size |
| ------------------- | ------------- | ----------------------------- | -------------: |
| CHITTI-Intent       | XLM-RoBERTa   | Desktop intent classification |     **500 MB** |
| CHITTI-Router       | XLM-RoBERTa   | Capability routing            |     **500 MB** |
| CHITTI-Presenter    | XLM-RoBERTa   | Presentation selection        |     **500 MB** |
| CHITTI-Memory       | TinyBERT      | Memory importance             |      **30 MB** |
| CHITTI-Tone         | TinyBERT      | Voice tone & humor            |      **30 MB** |
| CHITTI-Confidence   | TinyBERT      | Confidence estimation         |      **30 MB** |

---

# Total AI Stack for CHITTI MVP

| Model                          | Approx. Size |
| ------------------------------ | -----------: |
| openWakeWord                   |        10 MB |
| Silero VAD                     |         2 MB |
| Faster-Whisper Base            |        74 MB |
| XLM-RoBERTa                    |       500 MB |
| TinyBERT                       |        30 MB |
| BGE-M3                         |       2.2 GB |
| BGE-Reranker-v2-m3             |       2.2 GB |
| PaddleOCR                      |        25 MB |
| SmolVLM-256M                   |       256 MB |
| Gemma 3 1B *(or Qwen2.5-1.5B)* |        ~1 GB |

**Total runtime footprint:** **≈ 6.3 GB** (not all models need to be loaded simultaneously).

## My optimization recommendation

You don't actually need to keep all these models in memory. I would implement a **Model Manager** that loads models on demand:

* **Always loaded (≈50 MB):** openWakeWord, Silero VAD.
* **Conversation mode:** load Whisper + XLM-RoBERTa.
* **File search:** load BGE-M3.
* **Vision request:** load SmolVLM + PaddleOCR.
* **Unknown request or complex planning:** load Gemma 3 1B or Qwen2.5-1.5B.
* **After the task completes:** unload large models after a configurable idle timeout.

This keeps CHITTI lightweight while still providing all the capabilities you've planned.
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
