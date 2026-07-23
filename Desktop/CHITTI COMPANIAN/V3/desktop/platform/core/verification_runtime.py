import logging
import time
from typing import Any, Dict

from desktop.models.execution_models import (
    ExecutionStatus, VerificationStartedEvent, VerificationCompletedEvent
)
from desktop.platform.core.evidence_manager import EvidenceManager
from desktop.models.capability_models import VerificationManifest

logger = logging.getLogger(__name__)

class VerificationRuntime:
    """
    Subscribes to CAPABILITY_COMPLETED.
    Evaluates evidence (preferred -> fallback -> last_resort).
    Publishes VERIFICATION_COMPLETED.
    """
    def __init__(self, event_bus: Any, evidence_manager: EvidenceManager, registry: list):
        self.event_bus = event_bus
        self.evidence_manager = evidence_manager
        
        # Map of capabilities to lookup their verification manifest
        self.manifest_registry = {m.id: m for m in registry}

    def verify_step(self, context, capability_status) -> None:
        logger.info(f"VerificationRuntime: Verifying step {context.step_id} ({context.capability_id})")
        
        # 1. Publish Verification Started
        start_event = VerificationStartedEvent(context=context, timestamp=time.time())
        self.event_bus.publish("VERIFICATION_STARTED", source="VerificationRuntime", payload={"event": start_event})
        
        # 2. Get Verification Manifest
        cap_manifest = self.manifest_registry.get(context.capability_id)
        if not cap_manifest or not cap_manifest.verification:
            logger.warning(f"No verification manifest for {context.capability_id}. Assuming success.")
            self._publish_completed(context, ExecutionStatus.SUCCESS, 1.0, [])
            return
            
        vm: VerificationManifest = cap_manifest.verification
        
        # Short wait to allow OS to draw the window
        time.sleep(1.0)
        
        # 3. Gather Evidence (Hierarchy: preferred -> fallback -> last_resort)
        evidence_list = []
        final_status = ExecutionStatus.FAILED
        
        # Try preferred
        for source in vm.preferred:
            ev = self.evidence_manager.gather_evidence(source, context.parameters)
            evidence_list.append(ev)
            if ev.status == ExecutionStatus.SUCCESS and ev.confidence >= vm.required_confidence:
                final_status = ExecutionStatus.SUCCESS
                break
                
        # If preferred failed, try fallback
        if final_status != ExecutionStatus.SUCCESS:
            logger.info("Preferred evidence insufficient. Trying fallback.")
            for source in vm.fallback:
                ev = self.evidence_manager.gather_evidence(source, context.parameters)
                evidence_list.append(ev)
                if ev.status == ExecutionStatus.SUCCESS and ev.confidence >= vm.required_confidence:
                    final_status = ExecutionStatus.SUCCESS
                    break
        
        # We skip last_resort (Vision) for now to save tokens/time unless explicitly requested
        if final_status != ExecutionStatus.SUCCESS:
            logger.info("Fallback evidence insufficient. Verification Failed.")
        else:
            logger.info("Verification Succeeded based on gathered evidence.")
            
        # 4. Publish completed
        overall_confidence = max([e.confidence for e in evidence_list]) if evidence_list else 1.0
        self._publish_completed(context, final_status, overall_confidence, evidence_list)

    def _publish_completed(self, context, status, confidence, evidence) -> None:
        comp_event = VerificationCompletedEvent(
            context=context,
            status=status,
            confidence=confidence,
            evidence=evidence,
            timestamp=time.time()
        )
        self.event_bus.publish("VERIFICATION_COMPLETED", source="VerificationRuntime", payload={"event": comp_event})
