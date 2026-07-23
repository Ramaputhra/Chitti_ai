from typing import List, Dict, Any, Tuple
from desktop.models.activity import DocumentMemoryModel

class DocumentResolver:
    """
    Resolves "Open the proposal" to a specific DocumentMemoryModel.
    Combines Activity Memory, Semantic Search, Recent Files, and Metadata.
    """
    def resolve_document(self, query: str, context: Dict[str, Any]) -> Tuple[Optional[DocumentMemoryModel], float, List[Dict[str, Any]]]:
        # Placeholder for cross-system document scoring
        candidates = []
        
        if "proposal" in query.lower():
            # Mock candidate generation
            candidates.append({
                "document": DocumentMemoryModel(activity_type="Reading", document_path="Proposal_v3.pdf"),
                "score": 0.96,
                "reason": "Most recently modified and discussed yesterday."
            })
            candidates.append({
                "document": DocumentMemoryModel(activity_type="Reading", document_path="Proposal_Final.pdf"),
                "score": 0.82,
                "reason": "Lexical match, but older."
            })
            candidates.append({
                "document": DocumentMemoryModel(activity_type="Reading", document_path="Proposal_old.docx"),
                "score": 0.18,
                "reason": "Archived folder."
            })
            
        if not candidates:
            return None, 0.0, []
            
        candidates.sort(key=lambda x: x["score"], reverse=True)
        best = candidates[0]
        
        return best["document"], best["score"], candidates
