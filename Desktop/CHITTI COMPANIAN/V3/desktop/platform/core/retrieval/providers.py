from desktop.models.retrieval_provider import IRetrievalProvider
from desktop.models.retrieval import RetrievalQuery, RetrievalResult
from desktop.models.knowledge import KnowledgeFact

class SQLiteRetrievalProvider(IRetrievalProvider):
    """
    Searches explicit KnowledgeFacts stored in SQLite.
    Rule 289: LLMs never directly query this, RetrievalRuntime orchestrates it.
    """
    def provider_id(self) -> str: return "provider.retrieval.sqlite"
    
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        result = RetrievalResult(provider_id=self.provider_id())
        
        if query.include_facts:
            # Stub: fetch from Knowledge Repository based on text/entities
            fact = KnowledgeFact(
                id="f_stub",
                subject="example",
                predicate="retrieved_from",
                object="sqlite",
                source="SQLiteRetrievalProvider"
            )
            result.facts.append(fact)
            result.confidence = 1.0
            result.retrieval_trace = {"method": "text_match", "records_scanned": 100}
            
        return result

class MemoryRetrievalProvider(IRetrievalProvider):
    """
    Retrieves conversational memory and journal logs.
    """
    def provider_id(self) -> str: return "provider.retrieval.memory"
    
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        result = RetrievalResult(provider_id=self.provider_id())
        
        if query.include_memory:
            # Stub: fetch from IMemoryIndex
            result.sources.append("memory_journal")
            result.retrieval_trace = {"method": "semantic_memory", "episodes_found": 5}
            
        return result

class WorkspaceRetrievalProvider(IRetrievalProvider):
    """
    Retrieves currently opened files, project tech stack, and environment context.
    """
    def provider_id(self) -> str: return "provider.retrieval.workspace"
    
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        result = RetrievalResult(provider_id=self.provider_id())
        
        if query.include_workspace:
            # Stub: fetch active files
            result.sources.append("workspace_context")
            result.retrieval_trace = {"method": "active_editor", "files_found": 2}
            
        return result
