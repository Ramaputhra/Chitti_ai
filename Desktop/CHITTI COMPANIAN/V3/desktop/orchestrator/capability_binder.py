import time
from desktop.orchestrator.capability_manifest import CapabilityManifest, CapabilityLifecycleState
from desktop.brain.execution.models import ExecutionStepResult

class SecurityRejectionError(Exception):
    pass

class CapabilityExecutionException(Exception):
    pass

class CompatibilityLayer:
    def __init__(self, manifest: CapabilityManifest, v1_handler):
        self.manifest = manifest
        self.v1_handler = v1_handler
        self.state = CapabilityLifecycleState.REGISTERED
        self.retry_count = 0
        
    def initialize(self):
        self.state = CapabilityLifecycleState.READY
        
    def validate_security(self, confidence: float):
        if confidence < 0.8 and "destructive" in self.manifest.required_permissions:
            raise SecurityRejectionError(f"Confidence {confidence} too low for {self.manifest.capability_id}")
            
    def execute(self, params: dict, confidence: float) -> ExecutionStepResult:
        if self.state not in (CapabilityLifecycleState.READY, CapabilityLifecycleState.FAILED):
            raise CapabilityExecutionException(f"Capability not ready: {self.state}")
            
        self.validate_security(confidence)
        self.state = CapabilityLifecycleState.BUSY
        start_time = time.time()
        rollback_performed = False
        
        try:
            result_data = self.v1_handler(**params)
            duration_ms = int((time.time() - start_time) * 1000)
            self.state = CapabilityLifecycleState.READY
            
            return ExecutionStepResult(
                step_id="step_" + str(hash(time.time())),
                intent=self.manifest.semantic_intents[0] if self.manifest.semantic_intents else "unknown",
                status="COMPLETED",
                stdout=str(result_data),
                metadata={
                    "capability_id": self.manifest.capability_id,
                    "capability_version": self.manifest.capability_version,
                    "invocation_timestamp": start_time,
                    "execution_duration_ms": duration_ms,
                    "retry_count": self.retry_count,
                    "rollback_performed": rollback_performed
                }
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.retry_count += 1
            if self.manifest.supports_rollback:
                rollback_performed = True
                
            self.state = CapabilityLifecycleState.FAILED
            return ExecutionStepResult(
                step_id="step_err",
                intent=self.manifest.semantic_intents[0] if self.manifest.semantic_intents else "unknown",
                status="FAILED",
                stdout=f"Error: {str(e)}",
                metadata={
                    "capability_id": self.manifest.capability_id,
                    "capability_version": self.manifest.capability_version,
                    "invocation_timestamp": start_time,
                    "execution_duration_ms": duration_ms,
                    "retry_count": self.retry_count,
                    "rollback_performed": rollback_performed
                }
            )

class CapabilityBinder:
    def __init__(self, registry):
        self.registry = registry
        self.bindings = {}
        
    def register_v1_capability(self, manifest: CapabilityManifest, v1_handler):
        layer = CompatibilityLayer(manifest, v1_handler)
        layer.initialize()
        self.bindings[manifest.capability_id] = layer
        self.registry.register(manifest.capability_id, layer)
        return layer
