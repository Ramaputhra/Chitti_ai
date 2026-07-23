import time
from typing import List, Dict, Any, Optional
from desktop.models.memory import (
    Episode, MemoryEpisodeHint, ExperienceLevel, RetrievalConfig
)
from desktop.models.interaction import InteractionEnvelope

class MemoryRetrievalEngine:
    """
    COG-31A: Memory Retrieval & Selection Engine.
    Stateless pure engine composed internally by MemoryRuntime.
    Executes Two-Stage Retrieval:
    Stage 1: Indexed SQL / In-memory candidate pool fetching (bounded by candidate_pool_limit).
    Stage 2: In-memory scoring, pruning, continuous RetrievalConfidence computation,
             ExperienceLevel assignment, and Top-K MemoryEpisodeHint projection.
    """
    def __init__(self, config: Optional[RetrievalConfig] = None):
        self.config = config or RetrievalConfig()

    def calculate_semantic_similarity(self, user_payload: str, episode_intent: Any) -> float:
        """
        Computes semantic similarity score SimScore in [0.0, 1.0].
        Combines intent subtype matching and query/text string similarity.
        """
        if not user_payload or not episode_intent:
            return 0.0
            
        payload_lower = user_payload.strip().lower()
        
        # Extract intent query/subtype
        if isinstance(episode_intent, dict):
            intent_query = episode_intent.get("query", "") or episode_intent.get("subtype", "")
        else:
            intent_query = getattr(episode_intent, "query", "") or getattr(episode_intent, "subtype", "")
            
        intent_lower = str(intent_query).strip().lower()
        if not intent_lower:
            return 0.0

        # Exact match check
        if payload_lower == intent_lower:
            return 1.0

        # Substring / overlap similarity heuristic
        if intent_lower in payload_lower or payload_lower in intent_lower:
            return 0.85

        # Character/word token overlap similarity
        words_payload = set(payload_lower.split())
        words_intent = set(intent_lower.split())
        if not words_payload or not words_intent:
            return 0.0

        intersection = words_payload.intersection(words_intent)
        union = words_payload.union(words_intent)
        jaccard_sim = len(intersection) / len(union) if union else 0.0

        return min(1.0, max(0.0, round(jaccard_sim, 2)))

    def calculate_retrieval_confidence(
        self, sim_score: float, episode_score: float, episode_quality: float, fp_match: float = 1.0
    ) -> float:
        """
        COG-31A: Continuous metric C_retrieval in [0.0, 1.0].
        C_retrieval = 0.45 * SimScore + 0.25 * EpisodeScore + 0.15 * EpisodeQuality + 0.15 * FingerprintMatch
        """
        c_retrieval = (
            0.45 * sim_score +
            0.25 * min(1.0, max(0.0, episode_score)) +
            0.15 * min(1.0, max(0.0, episode_quality)) +
            0.15 * min(1.0, max(0.0, fp_match))
        )
        return min(1.0, max(0.0, round(c_retrieval, 4)))

    def assign_experience_level(self, confidence: float, is_fp_exact: bool = True) -> ExperienceLevel:
        """
        COG-31A: Maps continuous RetrievalConfidence metric to discrete ExperienceLevel policy abstraction.
        """
        if confidence >= 0.90 and is_fp_exact:
            return ExperienceLevel.EXACT
        elif confidence >= 0.75:
            return ExperienceLevel.HIGH
        elif confidence >= 0.60:
            return ExperienceLevel.MEDIUM
        elif confidence >= self.config.min_similarity_threshold:
            return ExperienceLevel.LOW
        else:
            return ExperienceLevel.NONE

    def retrieve_hints(
        self, interaction: InteractionEnvelope, candidates: List[Episode]
    ) -> List[MemoryEpisodeHint]:
        """
        Stage 2 Scoring, Pruning, Ranking, and Top-K Hint Selection.
        Consumes bounded candidate pool (M <= candidate_pool_limit).
        Returns Top-K anonymized MemoryEpisodeHint domain models.
        """
        if not candidates or not interaction:
            return []

        user_payload = interaction.payload or ""
        scored_hints = []

        # Stage 1 Pool Limit Enforcer
        bounded_pool = candidates[:self.config.candidate_pool_limit]

        for episode in bounded_pool:
            # Hard Pruning Filter 1: Verification Result
            ver_res = getattr(episode, "verification_result", None)
            ver_status = getattr(ver_res, "status", None)
            ver_status_str = getattr(ver_status, "name", str(ver_status)) if ver_status else ""
            
            # Skip failed verification episodes
            if ver_status_str and "FAIL" in ver_status_str.upper():
                continue

            # Compute Stage 2 Similarity
            sim_score = self.calculate_semantic_similarity(user_payload, getattr(episode, "intent", None))

            # Hard Pruning Filter 2: Minimum Similarity Threshold
            if sim_score < self.config.min_similarity_threshold:
                continue

            # Extract Score & Quality weights
            score_obj = getattr(episode, "episode_score", getattr(episode, "score", None))
            ep_score_val = getattr(score_obj, "score", 1.0) if score_obj else 1.0

            qual_obj = getattr(episode, "episode_quality", getattr(episode, "quality", None))
            ep_qual_val = getattr(qual_obj, "accuracy_confidence", getattr(qual_obj, "accuracy", 1.0)) if qual_obj else 1.0

            # Calculate continuous RetrievalConfidence
            confidence = self.calculate_retrieval_confidence(sim_score, ep_score_val, ep_qual_val, fp_match=1.0)

            # Assign ExperienceLevel
            exp_level = self.assign_experience_level(confidence, is_fp_exact=True)

            # Extract parameter summary
            plan_obj = getattr(episode, "execution_plan", None)
            workflows = getattr(plan_obj, "workflows", []) if plan_obj else []
            first_wf = workflows[0] if workflows else None
            wf_name = getattr(first_wf, "action", "Workflow") if first_wf else "Workflow"
            param_sum = getattr(first_wf, "parameters", {}) if first_wf else {}

            intent_sum = user_payload
            if isinstance(episode.intent, dict):
                intent_sum = episode.intent.get("query", user_payload)

            hint = MemoryEpisodeHint(
                intent_summary=intent_sum,
                verified_outcome="VERIFIED_SUCCESS",
                workflow_summary=wf_name,
                parameter_summary=param_sum,
                episode_score=ep_score_val,
                episode_quality=ep_qual_val,
                experience_level=exp_level,
                retrieval_confidence=confidence
            )
            scored_hints.append(hint)

        # Rank candidates by retrieval_confidence descending
        scored_hints.sort(key=lambda h: h.retrieval_confidence, reverse=True)

        # Stage 3: Top-K Selection
        return scored_hints[:self.config.top_k]
