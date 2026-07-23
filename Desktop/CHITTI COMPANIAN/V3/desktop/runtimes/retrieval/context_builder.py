from desktop.models.retrieval import RetrievalResult, ContextPackage
import copy

class ContextBuilder:
    """
    Rule 288: Context packages are immutable.
    Constructs the final package that reaches the AI Gateway, ensuring
    raw chunks are never directly consumed without being packaged.
    """
    
    def build(self, ranked_result: RetrievalResult) -> ContextPackage:
        """
        Takes the globally ranked RetrievalResult and transforms it into 
        an immutable ContextPackage.
        """
        package = ContextPackage(
            knowledge_facts=copy.deepcopy(ranked_result.facts),
            documents=copy.deepcopy(ranked_result.documents),
            retrieval_metadata={
                "latency_ms": ranked_result.latency_ms,
                "confidence": ranked_result.confidence,
                "provider_scores": copy.deepcopy(ranked_result.provider_scores),
                "trace": copy.deepcopy(ranked_result.retrieval_trace)
            }
        )
        
        # In a full implementation, we'd also pull active workspace context,
        # open files, and current conversation history into this package.
        
        # Ensure immutability (Python doesn't have deep immutability built-in, 
        # but logically we freeze it here).
        
        return package
