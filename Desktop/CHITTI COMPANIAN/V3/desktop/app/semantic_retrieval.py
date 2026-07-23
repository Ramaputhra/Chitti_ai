import math
from typing import List, Any
from abc import ABC, abstractmethod
from desktop.models.memory import MemorySnapshot, FactRecord, EpisodeRecord
from desktop.models.cognition import RetrievedMemory, RetrievalPolicy, SelectedContext
from desktop.models.interaction import InteractionEnvelope

class IEmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generates an embedding vector for the given text."""
        pass

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)

class SemanticRetrievalSelector:
    """
    Implements Rule 198: Retrieval Never Generates Data.
    Ranks memories strictly by semantic relevance.
    """
    def __init__(self, provider: IEmbeddingProvider, policy: RetrievalPolicy):
        self.provider = provider
        self.policy = policy
        
    async def retrieve(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> SelectedContext:
        query_vector = await self.provider.embed(interaction.payload)
        
        # We only apply semantic retrieval to Facts and Episodes.
        # Working memory and recent interactions bypass vector search (they're strictly chronological/active context).
        
        fact_results = self._rank_and_filter(memory.facts, query_vector)
        episode_results = self._rank_and_filter(memory.episodes, query_vector)
        # Graph Expansion (Rule 203)
        if self.policy.expansion_policy:
            fact_results = self._expand_graph(fact_results, memory)
            
        return SelectedContext(
            working_memory=[f"{wm.key}: {wm.value}" for wm in memory.working_memory],
            recent_messages=[m.content for m in memory.recent_interactions],
            facts=[f.memory.content for f in fact_results],
            episodes=[e.memory.summary for e in episode_results],
            session_context=memory.session_id,
            discarded_count=len(memory.facts) - len(fact_results) + len(memory.episodes) - len(episode_results)
        )
        
    def _rank_and_filter(self, items: List[Any], query_vector: List[float]) -> List[RetrievedMemory]:
        scored_items = []
        
        for item in items:
            if not item.embedding:
                continue # Skip items without embeddings (they should be indexed asynchronously)
                
            sim = cosine_similarity(query_vector, item.embedding)
            
            # Threshold Filter
            if sim >= self.policy.minimum_similarity:
                scored_items.append((sim, item))
                
        # Sort by similarity
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # Top-K Selection with Diversity
        top_k = []
        doc_counts = {}
        
        for sim, item in scored_items:
            if len(top_k) >= self.policy.maximum_candidates:
                break
                
            # Document Diversity logic
            if self.policy.diversity_enabled and hasattr(item, 'document_id') and item.document_id:
                doc_id = item.document_id
                count = doc_counts.get(doc_id, 0)
                if count >= self.policy.max_per_document:
                    continue # Skip this item to allow diversity
                doc_counts[doc_id] = count + 1
                
            top_k.append((sim, item))
        
        results = []
        for rank, (sim, item) in enumerate(top_k):
            reasons = [f"Semantic similarity = {sim:.2f}"]
            if hasattr(item, 'document_id') and item.document_id:
                reasons.append(f"Source Document = {item.document_id}")
            if hasattr(item, 'level'):
                reasons.append(f"Level = {item.level.value}")
                
            results.append(RetrievedMemory(
                memory=item,
                similarity=sim,
                rank=rank,
                retrieval_reason=", ".join(reasons)
            ))
            
        return results

    def _expand_graph(self, initial_results: List[RetrievedMemory], memory: MemorySnapshot) -> List[RetrievedMemory]:
        """
        Deterministically expands the retrieved nodes using the RetrievalExpansionPolicy.
        Only expands up to max_depth and maximum_expansion_nodes.
        """
        policy = self.policy.expansion_policy
        if not policy:
            return initial_results
            
        expanded = list(initial_results)
        retrieved_ids = {r.memory.record_id for r in initial_results if hasattr(r.memory, 'record_id')}
        expansion_count = 0
        
        # Simple BFS for depth=1
        for result in initial_results:
            if not hasattr(result.memory, 'record_id'):
                continue
                
            node_id = result.memory.record_id
            
            # Find relationships where this node is source or target
            for rel in memory.relationships:
                if expansion_count >= policy.maximum_expansion_nodes:
                    break
                    
                if rel.provenance.confidence < policy.minimum_confidence:
                    continue
                    
                if policy.allowed_relation_types and rel.relation_type not in policy.allowed_relation_types:
                    continue
                    
                target_id = None
                direction = ""
                if rel.source_record_id == node_id:
                    target_id = rel.target_record_id
                    direction = f"Outbound {rel.relation_type.value}"
                elif rel.target_record_id == node_id:
                    target_id = rel.source_record_id
                    direction = f"Inbound {rel.relation_type.value}"
                    
                if target_id and target_id not in retrieved_ids:
                    # Find the actual record in memory
                    target_record = next((f for f in memory.facts if getattr(f, 'record_id', None) == target_id), None)
                    if target_record:
                        retrieved_ids.add(target_id)
                        expansion_count += 1
                        expanded.append(RetrievedMemory(
                            memory=target_record,
                            similarity=result.similarity * rel.provenance.confidence, # Decayed similarity
                            rank=result.rank + 100, # Push lower in rank
                            retrieval_reason=f"Graph Expansion ({direction}) from node {node_id}"
                        ))
                        
        return expanded
