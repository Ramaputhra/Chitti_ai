from desktop.models.capability import CapabilityDescriptor, CapabilityParameter
from desktop.capabilities.files.document_parser import MarkItDownParser
from desktop.capabilities.files.chunk_builder import ChunkBuilder
from desktop.infrastructure.files.file_repository import FileRepository, KnowledgeStatus
from dataclasses import asdict

class DocumentIntelligenceCapability:
    def __init__(self):
        self.parser = MarkItDownParser()
        self.chunker = ChunkBuilder()
        self.repo = FileRepository()
        self.descriptor = CapabilityDescriptor(
            name="document_intelligence",
            description="Extracts content from documents (Rule 10). Does not invoke LLM directly.",
            parameters=[
                CapabilityParameter("path", "string", "The absolute file path to extract from"),
                CapabilityParameter("intent", "string", "What information is needed (e.g. summarize, find budget)", required=False)
            ]
        )
        
    async def invoke(self, params: dict):
        path = params.get("path")
        if not path:
            return {"status": "error", "message": "File path required."}
            
        # Check if exists
        if not self.repo.exists(path):
            return {"status": "error", "message": "File not found on disk."}
            
        # Extract content
        content = self.parser.extract(path)
        
        # Update Knowledge Status
        self.repo.update_knowledge_status(path, KnowledgeStatus.PARSED)
        
        # Chunk if needed
        chunks = self.chunker.chunk(content)
        
        # Return structured context to the Planner so it can formulate the final LLM request
        return {
            "status": "success",
            "context_type": "DocumentExtraction",
            "document_metadata": content.metadata,
            "page_count": content.page_count,
            "tables": content.tables,
            "sections": content.sections,
            "chunks": chunks
        }
