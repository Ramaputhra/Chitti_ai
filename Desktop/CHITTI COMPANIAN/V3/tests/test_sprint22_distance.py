from desktop.packages.desktop_pack.capabilities.distance import DistanceCapability

def run_tests():
    print("--- Running Sprint 22 Phase 1: Distance Capability E2E Regression ---")
    
    cap = DistanceCapability()
    output = cap.execute({"intent": "DistanceIntent", "origin": "Seattle", "destination": "Portland"})
    
    # 1. Execution
    assert output.execution_result.success is True, "Execution failed"
    assert output.execution_result.payload["destination"] == "Portland", "Destination payload mismatch"
    
    # 2. Verification
    assert output.verification_result.verified is True, "Verification failed"
    assert "geo_routing_api" in output.verification_result.evidence_ids, "Verification evidence mismatch"
    
    # 3. Conversation Artifact (Ensuring separation from live navigation)
    artifact = output.conversation_artifact
    assert artifact.artifact_type == "NavigationArtifact", "Artifact type mismatch (must be NavigationArtifact for Distance)"
    assert "Start Navigation" in artifact.supported_followup_actions, "Missing Navigation handoff affordance"
    assert artifact.presentation_available is True, "Presentation availability mismatch"
    
    # 4. Presentation
    pres = output.presentation_descriptor
    assert pres.experience_id == "exp_maps", "Presentation experience mismatch"
    assert pres.recipe_id == "recipe_route_overview", "Presentation recipe mismatch"
    
    # 5. Memory Integration (MemoryCandidate generation)
    mem = output.memory_candidate
    assert mem.activity_type == "Route Planning", "MemoryCandidate activity type mismatch"
    assert "Portland" in mem.related_entities, "MemoryCandidate entity mismatch"
    
    print("\n✓ Intent Resolution (Simulated)")
    print("✓ Planner Resolution (Simulated)")
    print("✓ Execution")
    print("✓ Verification")
    print("✓ ConversationArtifact generation")
    print("✓ Presentation compatibility")
    print("✓ Activity generation (via MemoryCandidate)")
    print("✓ MemoryCandidate generation")
    print("✓ Follow-up conversation (Start Navigation handoff validated)")
    print("\nDistance Capability successfully traversed the Core Architecture Spine!")

if __name__ == "__main__":
    run_tests()
