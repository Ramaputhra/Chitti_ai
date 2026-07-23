import asyncio
import uuid
from desktop.models.memory import KnowledgeCandidate, KnowledgeLevel, FactRecord, MemorySnapshot, SessionState
from desktop.app.knowledge_validator import KnowledgeValidator
from desktop.models.cognition import RetrievalPolicy
from desktop.app.semantic_retrieval import SemanticRetrievalSelector, IEmbeddingProvider
from desktop.models.interaction import InteractionEnvelope

class MockEmbeddingProvider(IEmbeddingProvider):
    async def embed(self, text: str) -> list[float]:
        if "architecture" in text.lower():
            return [1.0, 0.0, 0.0]
        else:
            return [0.0, 1.0, 0.0]

async def test_knowledge_pipeline():
    print("--- Running Sprint 91 Knowledge Pipeline Tests ---\n")
    
    # 1. Mocking markdown ingestion output (Knowledge Candidates)
    candidates = [
        # Hierarchy from Document 1 (Architecture)
        KnowledgeCandidate("Sprint 76 introduced the Runtime Kernel.", KnowledgeLevel.SUMMARY, 0.95, "doc1", "chunk1", "Summary extraction", {}),
        KnowledgeCandidate("Runtime Kernel handles lifecycle and composition.", KnowledgeLevel.CONCEPT, 0.9, "doc1", "chunk2", "Concept extraction", {}),
        KnowledgeCandidate("Runtime Kernel is deterministic.", KnowledgeLevel.ATOMIC_FACT, 0.98, "doc1", "chunk3", "Fact extraction", {}),
        KnowledgeCandidate("Planner is isolated.", KnowledgeLevel.ATOMIC_FACT, 0.95, "doc1", "chunk3", "Fact extraction", {}),
        KnowledgeCandidate("Capabilities are plugins.", KnowledgeLevel.ATOMIC_FACT, 0.92, "doc1", "chunk4", "Fact extraction", {}),
        KnowledgeCandidate("Memory uses embeddings.", KnowledgeLevel.ATOMIC_FACT, 0.91, "doc1", "chunk5", "Fact extraction", {}),
        # Bad provenance candidate
        KnowledgeCandidate("Ghost fact.", KnowledgeLevel.ATOMIC_FACT, 0.99, None, None, "Ghost", {}),
        
        # Hierarchy from Document 2 (Design Note)
        KnowledgeCandidate("UI themes use CSS.", KnowledgeLevel.ATOMIC_FACT, 0.9, "doc2", "chunk1", "Fact extraction", {})
    ]
    
    # 2. Validation (Rule 201: Provenance)
    validator = KnowledgeValidator(confidence_threshold=0.8)
    facts = validator.validate(candidates)
    
    # The 'Ghost fact' should be dropped due to lack of provenance
    assert len(facts) == 7
    print("✅ Test 1 & 4 (Validation & Provenance) passed. Ghost fact dropped.")
    
    # Check hierarchy
    levels = [f.level for f in facts]
    assert KnowledgeLevel.SUMMARY in levels
    assert KnowledgeLevel.CONCEPT in levels
    assert KnowledgeLevel.ATOMIC_FACT in levels
    print("✅ Test 3 (Hierarchy) passed.")
    
    # 3. Embed the valid facts
    provider = MockEmbeddingProvider()
    for f in facts:
        # We manually patch the embeddings since we don't have a real DB layer in this test
        sim = await provider.embed(f.content)
        # Using a hack to set frozen dataclass field for testing
        object.__setattr__(f, 'embedding', sim)
        
    memory = MemorySnapshot(
        session_id="test",
        session_state=SessionState.ACTIVE,
        recent_interactions=[],
        working_memory=[],
        facts=facts,
        episodes=[]
    )
    
    # 4. Semantic Retrieval with Diversity
    policy = RetrievalPolicy(
        minimum_similarity=0.5,
        maximum_candidates=10,
        minimum_results=1,
        allow_empty=True,
        fallback_strategy="heuristic",
        diversity_enabled=True,
        max_per_document=3 # Only allow max 3 items from doc1, even if they all match perfectly
    )
    
    selector = SemanticRetrievalSelector(provider, policy)
    query = InteractionEnvelope("q1", "Explain the architecture", {})
    
    result = await selector.retrieve(query, memory)
    
    # All 6 doc1 facts have vector [1.0, 0.0, 0.0] and match query [1.0, 0.0, 0.0] with sim 1.0.
    # But max_per_document is 3. So only 3 should be returned.
    doc1_results = [f for f in result.facts if "Runtime" in f or "Planner" in f or "Capabilities" in f or "Memory" in f or "Sprint" in f]
    
    assert len(doc1_results) == 3
    print("✅ Test 2 & 5 (Semantic Retrieval & Diversity) passed. Max 3 docs returned from doc1.")
    
    print("\n✅ All Sprint 91 tests passed.")

if __name__ == "__main__":
    asyncio.run(test_knowledge_pipeline())
