from desktop.orchestrator.capability_manifest import CapabilityManifest, CapabilityLifecycleState
from desktop.orchestrator.capability_binder import CapabilityBinder, CompatibilityLayer, SecurityRejectionError

class MockRegistry:
    def __init__(self):
        self.caps = {}
    def register(self, cid, layer):
        self.caps[cid] = layer

def mock_v1_browser_open(url=""):
    return f"Opened {url}"
    
def mock_v1_destructive():
    raise Exception("Physical Failure")

def run_verification():
    print("Starting EE3 Capability Execution Integration Verification...\n")
    
    print("[1/5] Instantiating Manifests & Binder...")
    registry = MockRegistry()
    binder = CapabilityBinder(registry)
    
    manifest_browser = CapabilityManifest(
        "com.chitti.browser", ["system.open_browser"], "1.0", [], {}, {}, False, 5000, True
    )
    manifest_destructive = CapabilityManifest(
        "com.chitti.delete", ["system.delete"], "1.0", ["destructive"], {}, {}, True, 5000, False
    )
    
    print("[2/5] Verifying Compatibility Layer Registration & Lifecycle...")
    layer_browser = binder.register_v1_capability(manifest_browser, mock_v1_browser_open)
    layer_delete = binder.register_v1_capability(manifest_destructive, mock_v1_destructive)
    
    assert layer_browser.state == CapabilityLifecycleState.READY
    print("       Capability successfully registered and transitioned to READY.")
    
    print("[3/5] Verifying Parameter Mapping & Result Normalization...")
    res = layer_browser.execute({"url": "http://example.com"}, 0.9)
    assert res.status == "COMPLETED"
    assert "Opened http://example.com" in res.stdout
    print("       Physical execution succeeded and normalized to ExecutionStepResult.")
    
    print("[4/5] Verifying Security Boundaries & Rollback Integration...")
    try:
        layer_delete.execute({}, 0.5)
        assert False, "Should have thrown SecurityRejectionError"
    except SecurityRejectionError:
        print("       SecurityRejectionError successfully blocked low-confidence destructive action.")
        
    res_fail = layer_delete.execute({}, 0.9)
    assert res_fail.status == "FAILED"
    assert res_fail.metadata["rollback_performed"] == True
    print("       Physical exception gracefully caught, rollback performed, returned FAILED status.")
    
    print("[5/5] Verifying Execution Provenance Metadata...")
    assert "capability_id" in res.metadata
    assert "invocation_timestamp" in res.metadata
    assert "execution_duration_ms" in res.metadata
    print(f"       Provenance verified: {res.metadata['capability_id']} executed in {res.metadata['execution_duration_ms']}ms.")
    
    print("\n✅ EE3 Capability Execution Architecture strictly verified.")

if __name__ == "__main__":
    run_verification()
