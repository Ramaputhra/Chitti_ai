import sys
import inspect
import importlib
import traceback

class Verifier:
    def __init__(self):
        self.failures = []
        self.passed = 0

    def assert_true(self, condition, error_msg):
        if not condition:
            self.failures.append(error_msg)
        else:
            self.passed += 1

def run_verification():
    v = Verifier()
    print("==========================================================")
    print("SPRINT 31B FINAL ENGINEERING VERIFICATION")
    print("==========================================================")

    # Check required modules
    try:
        mem_models = importlib.import_module("desktop.models.memory_episode")
        mem_comp = importlib.import_module("desktop.packages.desktop_pack.capabilities.memory_compiler")
        mem_run = importlib.import_module("desktop.brain.runtimes.memory_runtime")
        v.assert_true(True, "")
    except ImportError as e:
        v.assert_true(False, f"Required module missing: {e}")
        return v

    # Check classes
    from desktop.models.memory_episode import MemoryEpisode, MemoryEpisodeIdentity, MemoryConfidence, MemoryRelationships
    v.assert_true(inspect.isclass(MemoryEpisode), "MemoryEpisode missing")
    v.assert_true(inspect.isclass(MemoryEpisodeIdentity), "MemoryEpisodeIdentity missing")
    v.assert_true(inspect.isclass(MemoryConfidence), "MemoryConfidence missing")
    v.assert_true(inspect.isclass(MemoryRelationships), "MemoryRelationships missing")

    from desktop.packages.desktop_pack.capabilities.memory_compiler import MemoryCompilerCapability
    v.assert_true(inspect.isclass(MemoryCompilerCapability), "MemoryCompilerCapability missing")

    from desktop.brain.runtimes.memory_runtime import MemoryRuntime
    v.assert_true(inspect.isclass(MemoryRuntime), "MemoryRuntime missing")

    # Check Isolation
    source_comp = inspect.getsource(mem_comp)
    v.assert_true("sqlite3" not in source_comp, "MemoryCompiler must not use sqlite3.")
    v.assert_true("MemoryRuntime" not in source_comp, "MemoryCompiler must not import MemoryRuntime.")

    source_run = inspect.getsource(mem_run)
    v.assert_true("LLM" not in source_run and "openai" not in source_run.lower(), "MemoryRuntime must not perform cognitive reasoning.")

    # Execution Spine compatibility
    from desktop.platform.shared.interfaces.capability import ICapability
    v.assert_true(issubclass(MemoryCompilerCapability, ICapability), "MemoryCompilerCapability must inherit from ICapability")
    
    # End-to-end Behavioral Verification
    import os
    db_file = "test_verify_memory.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        
    try:
        from desktop.platform.shared.models.ai import ToolInvocation
        compiler = MemoryCompilerCapability()
        runtime = MemoryRuntime(db_path=db_file)
        
        experience_input = {
            "status": "READY_FOR_MEMORY",
            "experience_id": "exp_audit123",
            "fingerprint": "hash_audit456",
            "confidence": {"overall_score": 0.88},
            "reflection": {"summary": "Audit test reflection."}
        }
        
        # 1. Compile
        invocation = ToolInvocation(id="inv_test", tool_name="compile", arguments={"experience": experience_input}, confidence=1.0, source="test")
        output = compiler.execute(invocation)
        v.assert_true(output.execution_result.success, "Compiler failed execution.")
        
        payload = output.execution_result.payload
        v.assert_true(payload["status"] == "READY_FOR_PERSISTENCE", "Incorrect handoff state.")
        episode_dict = payload["episode"]
        
        # 2. Persist
        stored_id = runtime.persist(episode_dict)
        v.assert_true(stored_id == episode_dict['identity']['episode_id'], "Persistence ID mismatch.")
        
        # 3. Retrieve
        results = runtime.retrieve("Audit test reflection")
        v.assert_true(len(results) == 1, "Failed to retrieve episode.")
        retrieved = results[0]
        
        # 4. Reconstruct & Verify properties
        full = retrieved.get("full_payload", {})
        v.assert_true(full, "Full payload was not retrieved.")
        
        # Identity
        identity = full.get("identity", {})
        v.assert_true(identity.get("episode_id") == episode_dict["identity"]["episode_id"], "Identity.episode_id lost.")
        v.assert_true(identity.get("source_experience_id") == episode_dict["identity"]["source_experience_id"], "Identity.source_experience_id lost.")
        v.assert_true(identity.get("experience_fingerprint") == episode_dict["identity"]["experience_fingerprint"], "Identity.experience_fingerprint lost.")
        
        # Core Fields
        v.assert_true(full.get("semantic_summary") == episode_dict["semantic_summary"], "SemanticSummary lost.")
        v.assert_true(full.get("importance_score") == episode_dict["importance_score"], "ImportanceScore lost.")
        v.assert_true(full.get("retention_policy") == episode_dict["retention_policy"], "RetentionPolicy lost.")
        
        # Confidence
        confidence = full.get("confidence", {})
        v.assert_true(confidence.get("evidence_confidence") == episode_dict["confidence"]["evidence_confidence"], "Confidence.evidence_confidence lost.")
        v.assert_true(confidence.get("compiler_confidence") == episode_dict["confidence"]["compiler_confidence"], "Confidence.compiler_confidence lost.")
        
        # Relationships
        rels = full.get("relationships", {})
        v.assert_true(isinstance(rels, dict) and "parent_episodes" in rels, "Relationships lost.")
        
        # Metadata
        meta = full.get("metadata", {})
        v.assert_true(isinstance(meta, dict) and "domain_tags" in meta, "Metadata lost.")
        
        # Lifecycle
        v.assert_true(retrieved["state"] == "INDEXED", "Lifecycle state did not transition correctly.")
        
    except Exception as e:
        v.assert_true(False, f"Behavioral verification crashed: {traceback.format_exc()}")
        
    finally:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except:
                pass
    
    print("==========================================================")
    if v.failures:
        print(f"VERIFICATION FAILED: {len(v.failures)} issues found.")
        for f in v.failures:
            print(f" - {f}")
        print("Output: FAIL")
    else:
        print(f"VERIFICATION PASSED: All {v.passed} checks successful.")
        print("Sprint 31B implementation is verified.")
        print("Output: PASS")
    print("==========================================================")
    
if __name__ == "__main__":
    run_verification()
