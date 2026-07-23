from desktop.models.documents import DocumentContent
from typing import List

class ChunkBuilder:
    """
    Prevents redesign when users load huge PDFs.
    Chunks DocumentContent into LLM-digestible segments before handing back to Planner.
    """
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        
    def chunk(self, content: DocumentContent) -> List[str]:
        # MVP Mock implementation. In reality, we'd use a tokenizer (like tiktoken) 
        # to split content.markdown into overlapping chunks.
        text = content.markdown
        # Approx 4 chars per token
        max_chars = self.max_tokens * 4
        
        chunks = []
        for i in range(0, len(text), max_chars):
            chunks.append(text[i:i + max_chars])
            
        return chunks
