import logging
import time
import uuid
from typing import Dict, Any, Optional

from desktop.models.remote_provider import RemoteRequest, ProviderState
from desktop.models.routing_models import RoutingDecision, RoutingTrace, ExecutionTarget, PrivacyLevel
from desktop.platform.ai.provider_selector import ProviderSelector
from desktop.platform.ai.routing_telemetry import RoutingTelemetryPublisher

logger = logging.getLogger(__name__)

class AdaptiveAIRouter:
    """
    The central decision engine for AI routing.
    Evaluates policy, invokes the ProviderSelector, and orchestrates fallbacks.
    DOES NOT perform inference internally.
    """
    def __init__(self, 
                 execution_policy: Any, 
                 local_runtime: Any, 
                 remote_runtime: Any, 
                 provider_selector: ProviderSelector,
                 telemetry_publisher: RoutingTelemetryPublisher):
        
        self.execution_policy = execution_policy
        self.local_runtime = local_runtime
        self.remote_runtime = remote_runtime
        self.provider_selector = provider_selector
        self.telemetry_publisher = telemetry_publisher

    def route_request(self, request: RemoteRequest) -> Dict[str, Any]:
        """
        Main entry point for any AI Request in CHITTI.
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        trace = RoutingTrace(
            request_id=request_id,
            service=request.service,
            selected_runtime="NONE",
            selected_provider="NONE",
            decision_reason="Initialization",
            decision_confidence=0.0,
            execution_time_ms=0,
            status="PENDING"
        )
        
        try:
            # 1. Ask Execution Policy for the Target Runtime
            # (In reality, we'd build the context object using actual hardware profiles)
            # context = ExecutionPolicyContext(...)
            # target = self.execution_policy.evaluate_target(context)
            
            # Mocking the policy decision for this implementation
            target = ExecutionTarget.REMOTE 
            if request.privacy == "HIGH":
                target = ExecutionTarget.LOCAL
            
            # 2. Try Primary Target
            if target == ExecutionTarget.LOCAL:
                result = self._execute_local(request, trace)
                
            elif target == ExecutionTarget.REMOTE:
                result = self._execute_remote_with_fallback(request, trace)
                
            elif target == ExecutionTarget.OFFLINE_DEGRADED:
                trace.decision_reason = "System is Offline / Budget Exhausted"
                trace.decision_confidence = 1.0
                result = self._execute_local(request, trace)
            
            else:
                raise ValueError("Unknown target environment.")
                
            # Finish trace
            trace.status = "SUCCESS"
            trace.execution_time_ms = int((time.time() - start_time) * 1000)
            self.telemetry_publisher.publish_decision(trace)
            return result
            
        except Exception as e:
            logger.error(f"Routing failed for {request.service}: {e}")
            trace.status = "FAILED"
            trace.decision_reason = str(e)
            trace.execution_time_ms = int((time.time() - start_time) * 1000)
            self.telemetry_publisher.publish_decision(trace)
            
            # Return graceful AIResult instead of crashing
            return {
                "status": "graceful_fallback",
                "error": str(e),
                "message": "The AI service is currently unavailable."
            }
            
    def _execute_local(self, request: RemoteRequest, trace: RoutingTrace) -> Dict[str, Any]:
        trace.selected_runtime = "LOCAL"
        trace.selected_provider = "Qwen2.5-1.5B" # Example
        trace.decision_reason = "Local runtime selected by policy"
        trace.decision_confidence = 0.95
        logger.info(f"Routing {request.service} to LOCAL Runtime")
        # return self.local_runtime.execute(request)
        return {"status": "success", "runtime": "LOCAL", "data": "Local execution mock"}
        
    def _execute_remote_with_fallback(self, request: RemoteRequest, trace: RoutingTrace) -> Dict[str, Any]:
        trace.selected_runtime = "REMOTE"
        
        excluded = []
        while True:
            provider = self.provider_selector.select_best_provider(request, excluded_providers=excluded)
            
            if not provider:
                raise RuntimeError("No available remote providers could satisfy the request.")
                
            trace.selected_provider = provider.provider_id
            trace.decision_reason = f"ProviderSelector ranked {provider.provider_id} highest."
            trace.decision_confidence = 0.85
            logger.info(f"Routing {request.service} to REMOTE Runtime -> {provider.provider_id}")
            
            try:
                # return self.remote_runtime.execute(provider.provider_id, request)
                return {"status": "success", "runtime": "REMOTE", "provider": provider.provider_id}
            except Exception as e:
                logger.warning(f"Remote provider {provider.provider_id} failed: {e}. Attempting fallback...")
                excluded.append(provider.provider_id)
                trace.decision_reason = f"Fallback from {provider.provider_id} due to failure."
