from typing import Dict, Any, Optional
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.models.capability import (
    ExecutionResult, CanonicalCapabilityOutput, VerificationResult
)
from desktop.models.experience import Experience
from desktop.models.memory_episode import (
    MemoryEpisode, MemoryEpisodeIdentity, MemoryConfidence, 
    MemoryRelationships, MemoryEpisodeMetadata, RetentionPolicy
)

class MemoryCompilerCapability(ICapability):
    """
    Consumes a READY_FOR_MEMORY Experience and compiles it into a MemoryEpisode.
    Strictly responsible for cognition, NOT persistence.
    """
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        # 1. Ingestion: Retrieve the Experience from arguments
        experience_dict = invocation.arguments.get("experience", {})
        if not experience_dict:
            return self._fail("No Experience provided to MemoryCompiler.")
        
        status = experience_dict.get("status")
        if status != "READY_FOR_MEMORY":
            return self._fail(f"Invalid state: {status}. MemoryCompiler only accepts READY_FOR_MEMORY.")

        # 2. Eligibility & Deduplication
        fingerprint = experience_dict.get("fingerprint", "")
        # Minimal mock deduplication logic
        if not fingerprint:
            return self._fail("Experience lacks a deterministic fingerprint.")

        # 3. Compilation
        reflection = experience_dict.get("reflection", {})
        semantic_summary = reflection.get("summary", "Compiled memory summary.")
        
        # 4. Identity Generation
        identity = MemoryEpisodeIdentity(
            source_experience_id=experience_dict.get("experience_id", ""),
            compiler_version="v2.0.0",
            experience_fingerprint=fingerprint
        )

        # 5. Confidence Propagation
        # Pull minimum confidence from perceptual inputs
        confidence = MemoryConfidence(
            compiler_confidence=0.95,
            evidence_confidence=experience_dict.get("confidence", {}).get("overall_score", 1.0),
            retrieval_confidence=0.0
        )

        # 6. Metadata Extraction
        metadata = MemoryEpisodeMetadata(
            temporal_context=["AFTERNOON"],
            spatial_context=["CompilerWorkspace"],
            social_context=["System", "User"],
            domain_tags=["COGNITIVE_COMPILATION"]
        )

        # 7. Episode Generation
        episode = MemoryEpisode(
            semantic_summary=semantic_summary,
            identity=identity,
            confidence=confidence,
            metadata=metadata,
            relationships=MemoryRelationships(),
            importance_score=0.85,
            retention_policy=RetentionPolicy.LONG_TERM
        )

        # 8. Handoff
        import dataclasses
        
        # Serialize the dataclass completely
        episode_dict = dataclasses.asdict(episode)
        # Convert Enum to string for safe serialization
        episode_dict['retention_policy'] = episode.retention_policy.name

        return CanonicalCapabilityOutput(
            execution_result=ExecutionResult(
                success=True, 
                payload={"status": "READY_FOR_PERSISTENCE", "episode": episode_dict}
            ),
            verification_result=VerificationResult(verified=True, evidence_ids=[], verification_strategy="memory_compilation"),
            conversation_artifact=None,
            presentation_descriptor=None,
            memory_candidate=None
        )

    def _fail(self, reason: str) -> CanonicalCapabilityOutput:
        return CanonicalCapabilityOutput(
            execution_result=ExecutionResult(success=False, payload={"error": reason}),
            verification_result=VerificationResult(verified=False, evidence_ids=[], verification_strategy="memory_compilation"),
            conversation_artifact=None,
            presentation_descriptor=None,
            memory_candidate=None
        )
