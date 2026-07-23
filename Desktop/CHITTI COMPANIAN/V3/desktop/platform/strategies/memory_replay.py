import logging
import time
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field

from desktop.app.planner_contracts import IPlannerStrategy
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot, Episode
from desktop.models.environment import EnvironmentFingerprint
from desktop.models.cognition import (
    PlanningDecision, ExecutionPlan, WorkflowRequest, ApprovalRequirement, DecisionQuality, ExecutionPolicy
)

logger = logging.getLogger(__name__)

class MemoryReplayStrategy(IPlannerStrategy):
    """
    COG-31E: Episode Replay Engine Strategy.
    Evaluates historical Phase 3 Episode records for safe deterministic replay.
    Produces PlanningDecision recommendations for PlannerRuntime / HybridPlannerStrategy.
    Rule 18: DecisionEngine is pure.
    Rule 31: Capabilities & Strategies are stateless.
    Rule 33 & 36: Memory reads are cheap and strictly read-only.
    """
    def __init__(self, capability_registry=None, confidence_threshold: float = 0.70):
        self.capability_registry = capability_registry
        self.confidence_threshold = confidence_threshold

    def parse_intent(self, interaction: InteractionEnvelope, context: MemorySnapshot):
        """Step 1: Parse intent (Satisfies IPlannerStrategy interface)."""
        pass

    def formulate_decision(self, intent: Any, context: MemorySnapshot) -> PlanningDecision:
        """Step 2: Formulate decision (Satisfies IPlannerStrategy interface)."""
        pass

    def create_plan(self, decision: PlanningDecision, interaction: InteractionEnvelope, session_id: str) -> ExecutionPlan:
        """Step 3: Create plan (Satisfies IPlannerStrategy interface)."""
        pass

    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        """
        Main entry point for replay strategy evaluation.
        Retrieves candidates, checks eligibility and fingerprint, rebinds parameters,
        and returns a PlanningDecision recommendation with embedded explanation payload.
        """
        candidates = self._retrieve_candidates(interaction, memory)
        if not candidates:
            return self._build_rejected_decision("No historical episode candidates found.")

        current_fp = getattr(memory, "environment_fingerprint", None)
        if not current_fp:
            current_fp = EnvironmentFingerprint(
                fingerprint_id="current_fp",
                os_platform="Windows 11",
                screen_resolution="1920x1080",
                active_window="Desktop",
                timestamp=time.time()
            )

        best_candidate: Optional[Episode] = None
        best_confidence: float = 0.0
        best_explanation: Dict[str, Any] = {}
        best_rebound_plan: Optional[ExecutionPlan] = None

        for episode in candidates:
            eligible, confidence, explanation, rebound_plan = self._evaluate_eligibility(
                episode, interaction, current_fp
            )
            if eligible and confidence > best_confidence:
                best_candidate = episode
                best_confidence = confidence
                best_explanation = explanation
                best_rebound_plan = rebound_plan

        if not best_candidate or best_confidence < self.confidence_threshold:
            reason = best_explanation.get("reason", "No candidate met confidence threshold.")
            return self._build_rejected_decision(reason, explanation=best_explanation)

        # Formulate Decision Quality based on confidence score
        quality = DecisionQuality.CERTAIN if best_confidence >= 0.90 else DecisionQuality.UNCERTAIN

        decision = PlanningDecision(
            plan=best_rebound_plan,
            confidence=quality
        )
        # Attach explanation payload to decision (Refinement #2)
        setattr(decision, "explanation", best_explanation)
        setattr(decision, "replay_confidence_score", best_confidence)
        setattr(decision, "replayed_episode_id", best_candidate.episode_id)

        logger.info(f"[MemoryReplayStrategy] ✅ Recommended Replay for Episode {best_candidate.episode_id} (Score: {best_confidence:.2f})")
        return decision

    def _retrieve_candidates(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> List[Episode]:
        """
        Retrieves Phase 3 Episode records from MemorySnapshot (read-only projection).
        """
        candidates = []
        if hasattr(memory, "episodes") and memory.episodes:
            for item in memory.episodes:
                if isinstance(item, Episode):
                    candidates.append(item)
                elif isinstance(item, dict):
                    try:
                        candidates.append(Episode.from_dict(item))
                    except Exception:
                        pass
        return candidates

    def _evaluate_eligibility(
        self, episode: Episode, interaction: InteractionEnvelope, current_fp: EnvironmentFingerprint
    ) -> Tuple[bool, float, Dict[str, Any], Optional[ExecutionPlan]]:
        """
        Evaluates replay eligibility and calculates confidence score.
        Returns: (eligible: bool, confidence: float, explanation: dict, rebound_plan: ExecutionPlan)
        """
        explanation = {
            "intent_similarity": 0.0,
            "fingerprint_compatibility": 0.0,
            "episode_score": 0.0,
            "episode_quality": 0.0,
            "capability_availability": False,
            "reason": ""
        }

        # 1. Verification Result Check (Must be verified success)
        v_res = episode.verification_result
        v_success = False
        if isinstance(v_res, dict):
            v_status = v_res.get("status")
            v_success = (v_status in ["VERIFIED_SUCCESS", "VERIFICATION_NOT_SUPPORTED"])
        elif v_res and hasattr(v_res, "status"):
            v_status = getattr(v_res.status, "value", str(v_res.status))
            v_success = (v_status in ["VERIFIED_SUCCESS", "VERIFICATION_NOT_SUPPORTED"])

        if not v_success and v_res is not None:
            explanation["reason"] = "Historical episode verification failed."
            return False, 0.0, explanation, None

        # 2. Intent Similarity Check
        intent_similarity = self._calculate_intent_similarity(episode.intent, interaction)
        explanation["intent_similarity"] = intent_similarity
        if intent_similarity < 0.80:
            explanation["reason"] = f"Intent similarity too low ({intent_similarity:.2f} < 0.80)."
            return False, 0.0, explanation, None

        # 3. Environment Fingerprint Comparison (Hard & Soft Requirements)
        candidate_fp = episode.fingerprint
        if isinstance(candidate_fp, dict):
            candidate_fp = EnvironmentFingerprint.from_dict(candidate_fp)

        fp_ok, fp_score = self._compare_fingerprint(candidate_fp, current_fp)
        explanation["fingerprint_compatibility"] = fp_score
        if not fp_ok:
            explanation["reason"] = "Hard fingerprint requirements failed (OS or binary mismatch)."
            return False, 0.0, explanation, None

        # 4. Capability Availability Check
        plan_data = episode.execution_plan
        cap_avail = self._check_capability_availability(plan_data)
        explanation["capability_availability"] = cap_avail
        if not cap_avail:
            explanation["reason"] = "Required capabilities are not currently active in registry."
            return False, 0.0, explanation, None

        # 5. Score & Quality Metrics
        ep_score_val = episode.episode_score.score if episode.episode_score else 1.0
        ep_quality_val = episode.episode_quality.accuracy_confidence if episode.episode_quality else 1.0
        explanation["episode_score"] = ep_score_val
        explanation["episode_quality"] = ep_quality_val

        # 6. Overall Confidence Calculation
        confidence = (intent_similarity * 0.40) + (fp_score * 0.30) + (ep_score_val * 0.15) + (ep_quality_val * 0.15)

        # 7. Parameter Rebinding
        rebound_plan = self._rebind_parameters(plan_data, interaction)

        return True, confidence, explanation, rebound_plan

    def _calculate_intent_similarity(self, episode_intent: Any, interaction: InteractionEnvelope) -> float:
        """Calculates similarity between candidate intent and current interaction."""
        current_text = str(getattr(interaction, "payload", "") or "").lower().strip()
        
        ep_text = ""
        if isinstance(episode_intent, dict):
            ep_text = str(episode_intent.get("query", episode_intent.get("subtype", ""))).lower().strip()
        elif isinstance(episode_intent, str):
            ep_text = episode_intent.lower().strip()
            
        if not ep_text or not current_text:
            return 1.0 # Default fallback if intent schema is implicit
            
        if ep_text == current_text:
            return 1.0
        elif ep_text in current_text or current_text in ep_text:
            return 0.85
        return 0.50

    def _compare_fingerprint(
        self, candidate_fp: Optional[EnvironmentFingerprint], current_fp: EnvironmentFingerprint
    ) -> Tuple[bool, float]:
        """
        Classifies fingerprint attributes:
        - Hard Requirements: OS Platform match.
        - Soft Requirements: Active Window / Screen Resolution.
        - Optional Signals: Processes / Monitors.
        """
        if not candidate_fp or not current_fp:
            return True, 1.0 # Trivial match if fingerprint omitted

        # Hard Requirement: OS Platform
        if candidate_fp.os_platform and current_fp.os_platform:
            if candidate_fp.os_platform.lower() != current_fp.os_platform.lower():
                return False, 0.0

        score = 1.0
        # Soft Requirement: Resolution
        if candidate_fp.screen_resolution and current_fp.screen_resolution:
            if candidate_fp.screen_resolution != current_fp.screen_resolution:
                score -= 0.05

        # Soft Requirement: Active Window
        if candidate_fp.active_window and current_fp.active_window:
            if candidate_fp.active_window.lower() != current_fp.active_window.lower():
                score -= 0.10

        return True, max(score, 0.50)

    def _check_capability_availability(self, plan_data: Any) -> bool:
        """Checks if all actions in the plan are available in capability_registry."""
        if not self.capability_registry:
            return True # In absence of registry check, assume available

        workflows = []
        if isinstance(plan_data, dict):
            workflows = plan_data.get("workflows", [])
        elif hasattr(plan_data, "workflows"):
            workflows = getattr(plan_data, "workflows", [])

        for wf in workflows:
            action = wf.get("action") if isinstance(wf, dict) else getattr(wf, "action", "")
            if action:
                desc = None
                if hasattr(self.capability_registry, "resolve_by_action_name"):
                    desc = self.capability_registry.resolve_by_action_name(action)
                if not desc and hasattr(self.capability_registry, "resolve"):
                    desc = self.capability_registry.resolve(action)
                if not desc:
                    return False
        return True

    def _rebind_parameters(self, plan_data: Any, interaction: InteractionEnvelope) -> ExecutionPlan:
        """
        Rebinds parameters:
        - Static: Kept from stored ExecutionPlan.
        - Dynamic: Overridden with inputs from current InteractionEnvelope.
        - Runtime-Resolved: Marked for runtime evaluation.
        """
        workflows_rebound = []
        workflows = []
        if isinstance(plan_data, dict):
            workflows = plan_data.get("workflows", [])
        elif hasattr(plan_data, "workflows"):
            workflows = getattr(plan_data, "workflows", [])

        current_params = getattr(interaction, "parameters", {}) or getattr(interaction, "metadata", {}) or {}
        if not current_params and hasattr(interaction, "payload") and isinstance(interaction.payload, dict):
            current_params = interaction.payload

        for wf in workflows:
            action = wf.get("action") if isinstance(wf, dict) else getattr(wf, "action", "")
            corr_id = wf.get("correlation_id") if isinstance(wf, dict) else getattr(wf, "correlation_id", "")
            params = (wf.get("parameters") if isinstance(wf, dict) else getattr(wf, "parameters", {})) or {}
            
            # Rebind dynamic parameters from current interaction if available
            rebound_params = dict(params)
            if isinstance(current_params, dict):
                for k, v in current_params.items():
                    if k not in ["_tool_name"]:
                        rebound_params[k] = v

            workflows_rebound.append(
                WorkflowRequest(
                    action=action,
                    parameters=rebound_params,
                    policy=ExecutionPolicy(timeout=10.0),
                    correlation_id=corr_id or getattr(interaction, "id", "rebound_corr")
                )
            )

        return ExecutionPlan(
            approval=ApprovalRequirement(required=False, reason="Replay Authorization"),
            workflows=workflows_rebound
        )

    def _build_rejected_decision(self, reason: str, explanation: Optional[dict] = None) -> PlanningDecision:
        """Helper to create a rejected decision."""
        expl = explanation or {}
        expl["reason"] = reason
        decision = PlanningDecision(
            plan=ExecutionPlan(workflows=[]),
            confidence=DecisionQuality.REJECTED
        )
        setattr(decision, "explanation", expl)
        setattr(decision, "replay_confidence_score", 0.0)
        return decision
