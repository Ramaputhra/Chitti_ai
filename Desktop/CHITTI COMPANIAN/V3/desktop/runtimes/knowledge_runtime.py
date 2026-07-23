from desktop.models.knowledge import KnowledgeFact, KnowledgeQuery, KnowledgeLifecycle, KnowledgeConflict, KnowledgeResolutionStrategy
from desktop.models.knowledge_provider import KnowledgeCollectionTrigger
from desktop.models.knowledge_repository import IKnowledgeRepository
from desktop.runtimes.knowledge.validator import KnowledgeValidator
from desktop.runtimes.knowledge.provider_manager import ProviderManager

class KnowledgeRuntime:
    """
    The Knowledge Runtime manages the lifecycle, validation, and deterministic retrieval of facts.
    Rule 268: Never infers. Only stores, indexes, retrieves, versions, and validates.
    """

    def __init__(self, repository: IKnowledgeRepository, event_bus=None):
        self.repository = repository
        self.validator = KnowledgeValidator()
        self.provider_manager = ProviderManager()
        self.event_bus = event_bus

    async def handle_trigger(self, trigger: KnowledgeCollectionTrigger):
        """
        Rule 272: Runtime initiates collection. 
        Pulls data from providers based on the trigger.
        """
        self._emit("KnowledgeCollectionStarted", {"trigger": trigger.value})
        
        results = await self.provider_manager.trigger_collection(trigger)
        
        for result in results:
            for fact in result.facts:
                try:
                    self.store_fact(fact)
                except ValueError as e:
                    # In a full implementation, we'd route to ConflictResolver here
                    pass

        self._emit("KnowledgeCollectionCompleted", {"trigger": trigger.value})

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    def store_fact(self, fact: KnowledgeFact) -> bool:
        """Stores a new fact after validating it."""
        try:
            self.validator.validate_fact(fact)
            
            # Move through lifecycle
            fact.lifecycle = KnowledgeLifecycle.STORED
            success = self.repository.store_fact(fact)
            
            if success:
                self._emit("KnowledgeStored", {"fact_id": fact.id, "subject": fact.subject})
            return success
            
        except ValueError as e:
            self._emit("KnowledgeConflict", {"fact_id": fact.id, "error": str(e)})
            raise

    def update_fact(self, fact_id: str, new_fact: KnowledgeFact) -> bool:
        """
        Updates an existing fact by creating a new version (Rule 267).
        """
        existing_fact = self.repository.get_fact(fact_id)
        if not existing_fact:
            raise ValueError(f"Fact {fact_id} does not exist.")
            
        # Rule 267 Enforcement
        versioned_fact = self.validator.validate_update(existing_fact, new_fact)
        versioned_fact.lifecycle = KnowledgeLifecycle.STORED
        
        success = self.repository.update_fact(versioned_fact)
        if success:
            self._emit("KnowledgeUpdated", {"new_fact_id": versioned_fact.id, "supersedes_id": existing_fact.id})
        return success

    def query_facts(self, query: KnowledgeQuery) -> List[KnowledgeFact]:
        """
        Rule 270: Deterministic retrieval of facts.
        """
        return self.repository.query_facts(query)

    def archive_fact(self, fact_id: str) -> bool:
        """Moves a fact to ARCHIVED state instead of hard-deleting."""
        fact = self.repository.get_fact(fact_id)
        if fact:
            fact.lifecycle = KnowledgeLifecycle.ARCHIVED
            success = self.repository.update_fact(fact)
            if success:
                self._emit("KnowledgeArchived", {"fact_id": fact_id})
            return success
        return False
