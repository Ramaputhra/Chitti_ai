# CHITTI Engineering Decisions

This document records the rationale behind major architectural and engineering decisions. It serves as an immutable knowledge base to explain *why* the system was designed this way, preventing future redesigns from repeating old debates.

---

## Decision #001
**Title:** Inference Runtime is the only LLM caller.  
**Reason:** Centralizes prompt assembly and provider abstraction.  
**Alternatives:** Planner directly calling LLM.  
**Rejected because:** Violates separation of concerns. If the Planner formats prompts, changing LLM providers breaks the Planner.  
**Status:** Accepted.

---

## Decision #014
**Title:** Awareness is ephemeral; Memory stores validated knowledge.  
**Reason:** Raw window and process tracking events are too noisy and voluminous to store permanently.  
**Alternatives:** Storing all awareness events in a giant database.  
**Rejected because:** Creates massive bloat. The system must distill transient observations into semantic `WorkSession` episodes before permanent storage.  
**Status:** Accepted.

---

## Decision #027
**Title:** SessionRuntime interprets observations; AwarenessRuntime never interprets.  
**Reason:** Separates the objective collection of facts (Awareness) from the subjective semantic interpretation of those facts (Session/Intent).  
**Alternatives:** AwarenessRuntime directly detecting "Coding" or "Debugging" states.  
**Rejected because:** Blurs responsibilities. Interpretations evolve and change, while facts remain immutable. This guarantees Rule 38 (Observations Before Interpretation).  
**Status:** Accepted.

---

## Decision #034
**Title:** Conversation Context Expansion Precedes Intent Classification.
**Reason:** Resolving pronouns ("it", "the other one") and implicit commands ("Run", "Why?") cannot be done statelessly inside AIRuntime.
**Alternatives:** Forcing ClarificationIntent for all follow-up queries.
**Rejected because:** Degrades conversational fluidity. Instead, ConversationRuntime must intercept the raw utterance, resolve conversational artifacts (pronouns/targets), and generate an Expanded Semantic Request *before* invoking AIRuntime for Intent Classification.
**Status:** Accepted (Sprint 18.5).
