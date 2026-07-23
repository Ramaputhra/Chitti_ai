import asyncio
from desktop.models.memory import KnowledgeLevel, RelationType, MemorySnapshot, SessionState
from desktop.models.cognition import ExtractedKnowledgeGraph, TemporaryNode, TemporaryRelationship, RetrievalPolicy, RetrievalExpansionPolicy
from desktop.app.knowledge_validator import KnowledgeValidator
from desktop.app.semantic_retrieval import SemanticRetrievalSelector, IEmbeddingProvider
from desktop.models.interaction import InteractionEnvelope

class MockEmbeddingProvider(IEmbeddingProvider):
    async def embed(self, text: str) -> list[float]:
        # Simple mock
        return [1.0, 0.0, 0.0]

async def test_knowledge_graph():
    print("--- Running Sprint 92 Knowledge Graph Tests ---\n")
    
    # 1. Mocking LLM output: ExtractedKnowledgeGraph with temporary IDs
    graph = ExtractedKnowledgeGraph(
        nodes=[
            TemporaryNode("_node_1", "Architecture Rule", KnowledgeLevel.CONCEPT, 0.9, "doc1", "chunk1", ""),
            TemporaryNode("_node_2", "Runtime Kernel", KnowledgeLevel.CONCEPT, 0.95, "doc1", "chunk1", ""),
            TemporaryNode("_node_3", "Bad Fact", KnowledgeLevel.ATOMIC_FACT, 0.3, "doc1", "chunk2", ""), # Low confidence
            TemporaryNode("_node_4", "Lifecycle", KnowledgeLevel.ATOMIC_FACT, 0.9, "doc1", "chunk3", "")
        ],
        edges=[
            TemporaryRelationship("_node_1", "_node_2", RelationType.DEPENDS_ON, 0.8, ""),
            TemporaryRelationship("_node_2", "_node_4", RelationType.IMPLEMENTS, 0.8, ""),
            TemporaryRelationship("_node_1", "_node_3", RelationType.REFERENCES, 0.9, ""), # Edge to rejected node
            TemporaryRelationship("_node_2", "_node_1", RelationType.USES, 0.2, ""), # Low confidence edge
            TemporaryRelationship("_node_4", "_node_4", RelationType.PART_OF, 0.9, "") # Self reference
        ],
        metadata={
            "source_id": "doc1",
            "extractor": "MockLLM"
        }
    )
    
    # 2. Validation
    validator = KnowledgeValidator(node_confidence_threshold=0.5, edge_confidence_threshold=0.5)
    records, relationships = validator.validate(graph)
    
    # Test 1: Temporary IDs resolve to UUIDs
    assert len(records) == 3 # _node_3 is dropped
    assert all(len(r.record_id) > 10 for r in records) # They are UUIDs
    print("✅ Test 1 (UUID Resolution) passed.")
    
    # Test 2 & 3: Relationships survive, dangling edges drop, low confidence edges drop, self-references drop
    assert len(relationships) == 2
    rel_types = [r.relation_type for r in relationships]
    assert RelationType.DEPENDS_ON in rel_types
    assert RelationType.IMPLEMENTS in rel_types
    assert RelationType.REFERENCES not in rel_types # dangling
    assert RelationType.USES not in rel_types # low confidence
    assert RelationType.PART_OF not in rel_types # self reference
    print("✅ Test 2 & 3 & 5 (Relationship Validation) passed.")
    
    # 3. Setup Memory for Retrieval Expansion
    provider = MockEmbeddingProvider()
    for r in records:
        # Patch embedding
        object.__setattr__(r, 'embedding', [1.0, 0.0, 0.0])
        
    memory = MemorySnapshot(
        session_id="test",
        session_state=SessionState.ACTIVE,
        recent_interactions=[],
        working_memory=[],
        facts=records,
        relationships=relationships,
        episodes=[]
    )
    
    # We want to retrieve Node 1, and ensure Node 2 is expanded.
    policy = RetrievalPolicy(
        minimum_similarity=0.5,
        maximum_candidates=1, # Only retrieve 1 node directly
        minimum_results=1,
        allow_empty=True,
        fallback_strategy="heuristic",
        expansion_policy=RetrievalExpansionPolicy(
            max_depth=1,
            maximum_expansion_nodes=5,
            minimum_confidence=0.5
        )
    )
    
    selector = SemanticRetrievalSelector(provider, policy)
    query = InteractionEnvelope("q1", "dummy", {})
    
    result = await selector.retrieve(query, memory)
    
    # The initial retrieval grabbed 1 node. Expansion should have grabbed its neighbor.
    assert len(result.facts) == 2
    # Verify the reason mentions expansion
    assert any("Graph Expansion" in r for r in result.facts)
    print("✅ Test 4 (Retrieval Expansion) passed.")
    
    print("\n✅ All Sprint 92 tests passed.")

if __name__ == "__main__":
    asyncio.run(test_knowledge_graph())
