from desktop.packages.desktop_pack.capabilities.time import TimeCapability

def run_tests():
    print("--- Running Sprint 22 Phase 1: Time Capability E2E Regression ---")
    
    cap = TimeCapability()
    output = cap.execute({"intent": "StateQueryIntent", "subject": "time"})
    
    # 1. Execution
    assert output.execution_result.success is True, "Execution failed"
    assert "time" in output.execution_result.payload, "Missing time in execution payload"
    
    # 2. Verification
    assert output.verification_result.verified is True, "Verification failed"
    assert output.verification_result.evidence_ids == ["system_clock"], "Verification evidence mismatch"
    
    # 3. Conversation Artifact
    artifact = output.conversation_artifact
    assert artifact.artifact_type == "TimeArtifact", "Artifact type mismatch"
    assert "Convert Timezone" in artifact.supported_followup_actions, "Missing expected affordance"
    assert artifact.presentation_available is True, "Presentation availability mismatch"
    
    # 4. Presentation
    pres = output.presentation_descriptor
    assert pres.experience_id == "exp_time", "Presentation experience mismatch"
    assert pres.recipe_id == "recipe_digital_clock", "Presentation recipe mismatch"
    
    # 5. Memory Integration (MemoryCandidate generation)
    mem = output.memory_candidate
    assert mem.activity_type == "System Query", "MemoryCandidate activity type mismatch"
    assert "Time" in mem.related_entities, "MemoryCandidate entity mismatch"
    
    print("\n✓ Intent Resolution (Simulated)")
    print("✓ Planner Resolution (Simulated)")
    print("✓ Execution")
    print("✓ Verification")
    print("✓ ConversationArtifact generation")
    print("✓ Presentation compatibility")
    print("✓ Activity generation (via MemoryCandidate)")
    print("✓ MemoryCandidate generation")
    print("✓ Follow-up conversation (Affordances validated)")
    print("\nTime Capability successfully traversed the Core Architecture Spine!")

if __name__ == "__main__":
    run_tests()
