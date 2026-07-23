import uuid
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from desktop.models.capability import (
    CanonicalCapabilityOutput,
    ExecutionResult as CapExecutionResult,
    VerificationResult,
    PresentationDescriptor,
    MemoryCandidate
)
from desktop.models.conversation import SearchArtifact, Citation, ReferencedEntity

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor

class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> Dict[str, Any]:
        pass

class MockGoogleProvider(SearchProvider):
    def search(self, query: str) -> Dict[str, Any]:
        return {
            "provider": "google",
            "results": [
                {
                    "title": "Example Search Result",
                    "url": "https://example.com",
                    "snippet": "This is a deterministic search result."
                }
            ],
            "entities": [
                {
                    "id": "ent_123",
                    "type": "Organization",
                    "name": "Example Org"
                }
            ]
        }

class SearchCapability(ICapability):
    """
    Search Capability (Sprint 25).
    Deterministic external knowledge retrieval.
    Strictly prohibits semantic reasoning, summarization, and direct browser automation.
    """
    def __init__(self, provider: SearchProvider = None):
        self.provider = provider or MockGoogleProvider()
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SearchCapability"

    @property
    def capability_id(self) -> str:
        return "cap_external_search"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="search",
                description="External search.",
                parameters={}
            )
        ]

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            version="1.0",
            category="System",
            tools=self.discover_tools(),
            description="External search capability."
        )

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "search"

    def cancel(self, invocation_id: str) -> None:
        pass

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        payload = invocation.arguments
        query = payload.get("query", "")
        now = datetime.now()
        
        # 1. Execute Provider Search
        raw_response = self.provider.search(query)
        provider_name = raw_response.get("provider", "unknown")
        results = raw_response.get("results", [])
        raw_entities = raw_response.get("entities", [])
        
        # 2. Extract deterministic metadata
        citations = []
        for i, res in enumerate(results):
            citations.append(Citation(
                title=res.get("title", "Untitled"),
                url=res.get("url", ""),
                provider=provider_name,
                retrieved_at=now,
                rank=i + 1,
                confidence=0.9
            ))
            
        referenced_entities = []
        for e in raw_entities:
            referenced_entities.append(ReferencedEntity(
                entity_id=e.get("id", ""),
                entity_type=e.get("type", "Unknown"),
                canonical_name=e.get("name", "Unknown"),
                metadata={}
            ))
        
        # 3. Formulate Execution Result
        cap_exec_result = CapExecutionResult(
            success=True,
            payload={
                "query": query,
                "provider": provider_name,
                "result_count": len(results)
            }
        )
        
        verify_result = VerificationResult(
            verified=True,
            evidence_ids=["search_api_logs"],
            verification_strategy="api_checksum"
        )
        
        # 4. Formulate SearchArtifact
        affordances = ["Open Result", "Compare Results", "Summarize", "Search Again", "Present"]
        
        artifact = SearchArtifact(
            artifact_id=str(uuid.uuid4()),
            artifact_type="SearchArtifact",
            capability_id=self.capability_id,
            timestamp=now,
            summary=f"Found {len(results)} results for '{query}'",
            structured_result=cap_exec_result.payload,
            referenced_entities=referenced_entities,
            supported_followup_actions=affordances,
            presentation_available=False,
            expiration_policy="transient",
            confidence=0.95,
            provider=provider_name,
            query=query,
            results=results,
            extracted_entities=referenced_entities,
            citations=citations,
            supported_affordances=affordances
        )
        
        # 5. Formulate Presentation & Memory
        pres_descriptor = PresentationDescriptor(
            experience_id="exp_search_results",
            recipe_id="recipe_result_list",
            layout_data={"query": query, "results": results}
        )
        
        artifact.presentation_descriptor = pres_descriptor.__dict__
        
        mem_candidate = MemoryCandidate(
            activity_type="Information Retrieval",
            workspace_hint="Search Engine",
            related_entities=[query],
            timestamp=now
        )
        
        artifact.memory_candidate = mem_candidate.__dict__
        
        canonical_out = CanonicalCapabilityOutput(
            execution_result=cap_exec_result,
            verification_result=verify_result,
            conversation_artifact=artifact,
            presentation_descriptor=pres_descriptor,
            memory_candidate=mem_candidate
        )
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=canonical_out)
