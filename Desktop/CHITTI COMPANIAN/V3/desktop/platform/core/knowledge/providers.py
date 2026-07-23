import uuid
from typing import List
from desktop.models.knowledge import KnowledgeFact, KnowledgeNamespace, KnowledgeSource
from desktop.models.knowledge_provider import (
    IKnowledgeProvider, KnowledgeProviderDescriptor, 
    KnowledgeCollectionTrigger, RefreshPolicy, KnowledgeCollectionResult
)

class SystemKnowledgeProvider(IKnowledgeProvider):
    def descriptor(self) -> KnowledgeProviderDescriptor:
        return KnowledgeProviderDescriptor(
            provider_id="provider.system.local",
            name="System Environment Provider",
            version="1.0.0",
            namespaces=[KnowledgeNamespace.SYSTEM],
            priority=100,
            refresh_policy=RefreshPolicy.EVENT,
            supports_manual_refresh=True,
            supports_incremental=False
        )

    async def collect(self, trigger: KnowledgeCollectionTrigger) -> KnowledgeCollectionResult:
        result = KnowledgeCollectionResult()
        if trigger in [KnowledgeCollectionTrigger.SYSTEM_STARTUP, KnowledgeCollectionTrigger.MANUAL_REFRESH]:
            # Stub: collect OS, Python, GPU facts
            fact = KnowledgeFact(
                id=str(uuid.uuid4()),
                fact_root_id="sys_os_platform",
                subject="system",
                predicate="os",
                object="Windows",
                confidence=1.0,
                source=KnowledgeSource.SYSTEM,
                namespace=KnowledgeNamespace.SYSTEM
            )
            result.facts.append(fact)
        return result

    async def refresh(self) -> None:
        pass


class WorkspaceKnowledgeProvider(IKnowledgeProvider):
    def descriptor(self) -> KnowledgeProviderDescriptor:
        return KnowledgeProviderDescriptor(
            provider_id="provider.workspace.analyzer",
            name="Workspace Analyzer Provider",
            version="1.0.0",
            namespaces=[KnowledgeNamespace.WORKSPACE],
            priority=80,
            refresh_policy=RefreshPolicy.EVENT,
            supports_manual_refresh=True,
            supports_incremental=True
        )

    async def collect(self, trigger: KnowledgeCollectionTrigger) -> KnowledgeCollectionResult:
        result = KnowledgeCollectionResult()
        # Stub: collect dependencies, languages, open documents
        return result

    async def refresh(self) -> None:
        pass


class MemoryKnowledgeProvider(IKnowledgeProvider):
    def descriptor(self) -> KnowledgeProviderDescriptor:
        return KnowledgeProviderDescriptor(
            provider_id="provider.memory.extractor",
            name="Memory Facts Extractor",
            version="1.0.0",
            namespaces=[KnowledgeNamespace.USER],
            priority=50,
            refresh_policy=RefreshPolicy.EVENT,
            supports_manual_refresh=False,
            supports_incremental=True
        )

    async def collect(self, trigger: KnowledgeCollectionTrigger) -> KnowledgeCollectionResult:
        result = KnowledgeCollectionResult()
        # Rule 271: Never infers. Only extracts explicitly marked preferences from journal.
        return result

    async def refresh(self) -> None:
        pass
