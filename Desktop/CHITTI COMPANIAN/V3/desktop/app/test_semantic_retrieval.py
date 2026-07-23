import asyncio
from desktop.models.memory import MemorySnapshot, FactRecord, EpisodeRecord, SessionState
from desktop.models.cognition import RetrievalPolicy
from desktop.models.interaction import InteractionEnvelope
from desktop.app.semantic_retrieval import SemanticRetrievalSelector, IEmbeddingProvider

class MockEmbeddingProvider(IEmbeddingProvider):
    async def embed(self, text: str) -> list[float]:
        # Simple mock: just return a fake vector based on some keyword matching for testing cosine similarity
        if "weather" in text.lower():
            return [1.0, 0.0, 0.0]
        elif "wife" in text.lower() or "birthday" in text.lower():
            return [0.0, 1.0, 0.0]
        else:
            return [0.0, 0.0, 1.0]

async def test_semantic_retrieval():
    policy = RetrievalPolicy(
        minimum_similarity=0.5,
        maximum_candidates=2,
        minimum_results=1,
        allow_empty=True,
        fallback_strategy="heuristic"
    )
    
    provider = MockEmbeddingProvider()
    selector = SemanticRetrievalSelector(provider, policy)
    
    memory = MemorySnapshot(
        session_id="test-session",
        session_state=SessionState.ACTIVE,
        recent_interactions=[],
        working_memory=[],
        facts=[
            FactRecord(
                fact_id="1", 
                content="My wife's birthday is October 12.", 
                source_interaction_id="a", 
                confidence=1.0,
                embedding=[0.0, 0.9, 0.1], # Very similar to "wife" query
                embedding_metadata=None
            ),
            FactRecord(
                fact_id="2",
                content="The weather in Paris is usually nice in spring.",
                source_interaction_id="b",
                confidence=1.0,
                embedding=[0.9, 0.0, 0.1], # Very similar to "weather" query
                embedding_metadata=None
            ),
            FactRecord(
                fact_id="3",
                content="I need to buy a gift for my wife.",
                source_interaction_id="c",
                confidence=0.9,
                embedding=[0.0, 0.8, 0.2], # Also similar to "wife", but slightly less
                embedding_metadata=None
            )
        ]
    )
    
    # Test 1: Query about wife's birthday
    query = InteractionEnvelope(interaction_id="x", payload="What is my wife's birthday?", metadata={})
    result = await selector.retrieve(query, memory)
    
    assert len(result.facts) == 2 # Max candidates is 2
    assert "birthday" in result.facts[0] # The 0.9 match should be first
    assert "gift" in result.facts[1] # The 0.8 match should be second
    assert result.discarded_count == 1 # The weather fact is discarded
    
    # Test 2: Query about weather
    query2 = InteractionEnvelope(interaction_id="y", payload="Tell me the weather", metadata={})
    result2 = await selector.retrieve(query2, memory)
    
    assert len(result2.facts) == 1 # Only weather fact passes threshold
    assert "weather" in result2.facts[0]
    assert result2.discarded_count == 2
    
    print("✅ Semantic Retrieval tests passed")

if __name__ == "__main__":
    print("--- Running Semantic Retrieval Tests (Sprint 90) ---\n")
    asyncio.run(test_semantic_retrieval())
    print("\n✅ All Sprint 90 tests passed.")
