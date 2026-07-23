import sys
import inspect
import importlib
import builtins
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
    print("SPRINT 31A FINAL ENGINEERING VERIFICATION")
    print("==========================================================")

    # 1. Check required Python modules exist
    print("[1] Checking required Python modules...")
    try:
        experience_models = importlib.import_module("desktop.models.experience")
        experience_capabilities = importlib.import_module("desktop.packages.desktop_pack.capabilities.experience_intelligence")
        v.assert_true(True, "")
    except ImportError as e:
        v.assert_true(False, f"Required module missing: {e}")
        return v

    # 2. Check required classes and dataclasses exist
    print("[2] Checking required classes and dataclasses...")
    from desktop.models.experience import (
        Experience, ExplainableConfidence, SemanticScoring
    )
    v.assert_true(inspect.isclass(Experience), "Experience model is missing or not a class.")
    
    # 5. Verify ExplainableConfidence, SemanticScoring and ExperienceFingerprint exist
    print("[3] Verifying specific models (ExplainableConfidence, SemanticScoring, ExperienceFingerprint)...")
    v.assert_true(inspect.isclass(ExplainableConfidence), "ExplainableConfidence model is missing.")
    v.assert_true(inspect.isclass(SemanticScoring), "SemanticScoring model is missing.")
    # The fingerprint might just be a property, but let's check if Experience has it
    v.assert_true(hasattr(Experience, "fingerprint") or 'fingerprint' in Experience.__annotations__, "Experience is missing 'fingerprint' attribute.")

    # 3. Check Capabilities are implemented
    print("[4] Checking core Capabilities...")
    from desktop.packages.desktop_pack.capabilities.experience_intelligence import (
        ExperienceBuilderCapability, ExperienceReflectionCapability, ExperienceValidatorCapability
    )
    v.assert_true(inspect.isclass(ExperienceBuilderCapability), "ExperienceBuilderCapability missing.")
    v.assert_true(inspect.isclass(ExperienceReflectionCapability), "ExperienceReflectionCapability missing.")
    v.assert_true(inspect.isclass(ExperienceValidatorCapability), "ExperienceValidatorCapability missing.")

    # 6. Verify Execution Spine compatibility
    print("[5] Verifying Execution Spine compatibility...")
    from desktop.platform.shared.interfaces.capability import ICapability
    v.assert_true(issubclass(ExperienceBuilderCapability, ICapability), "ExperienceBuilderCapability does not inherit from ICapability.")
    v.assert_true(hasattr(ExperienceBuilderCapability, "execute"), "ExperienceBuilderCapability lacks 'execute' method.")

    # 7. Verify Memory isolation (no storage/retrieval implemented)
    print("[6] Verifying Memory isolation (no MemoryRuntime or DB access)...")
    source_code = inspect.getsource(experience_capabilities)
    v.assert_true("MemoryRuntime" not in source_code, "Memory isolation violated: MemoryRuntime referenced in capabilities.")
    v.assert_true("sqlite3" not in source_code, "Memory isolation violated: DB access referenced in capabilities.")
    v.assert_true("insert" not in source_code.lower() and "update" not in source_code.lower() and "select" not in source_code.lower(), "Memory isolation violated: SQL operations found.")

    # 4 & 8. Verify the READY_FOR_MEMORY lifecycle and execute minimal end-to-end pipeline
    print("[7] Executing minimal end-to-end pipeline...")
    try:
        from desktop.platform.shared.models.ai import ToolInvocation
        import uuid
        
        def create_invocation(tool_name):
            return ToolInvocation(
                id=f"inv_{uuid.uuid4().hex[:8]}",
                tool_name=tool_name,
                arguments={},
                confidence=1.0,
                source="Verifier"
            )

        builder = ExperienceBuilderCapability()
        reflector = ExperienceReflectionCapability()
        validator = ExperienceValidatorCapability()

        print("    -> Running Builder...")
        r1 = builder.execute(create_invocation("experience_build"))
        
        print("    -> Running Reflector...")
        r2 = reflector.execute(create_invocation("experience_reflect"))
        
        print("    -> Running Validator...")
        r3 = validator.execute(create_invocation("experience_validate"))

        final_status = r3.execution_result.payload.get("status")
        print(f"    -> Final Status: {final_status}")
        v.assert_true(final_status == "READY_FOR_MEMORY", f"Lifecycle failed: expected READY_FOR_MEMORY, got {final_status}")
        
    except Exception as e:
        v.assert_true(False, f"End-to-end pipeline crashed: {traceback.format_exc()}")

    print("==========================================================")
    if v.failures:
        print(f"VERIFICATION FAILED: {len(v.failures)} issues found.")
        for f in v.failures:
            print(f" - {f}")
    else:
        print(f"VERIFICATION PASSED: All {v.passed} checks successful.")
        print("Sprint 31A architecture is verified.")
    print("==========================================================")
    
if __name__ == "__main__":
    run_verification()
