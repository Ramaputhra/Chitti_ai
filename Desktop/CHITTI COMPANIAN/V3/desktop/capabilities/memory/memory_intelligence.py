from desktop.models.capability import CapabilityDescriptor, CapabilityParameter
from desktop.runtimes.memory_runtime import MemoryRuntime
from desktop.models.memory import Fact, MemorySource, FactStatus
import time

class MemoryIntelligenceCapability:
    def __init__(self, runtime: MemoryRuntime):
        self.runtime = runtime
        self.descriptor = CapabilityDescriptor(
            name="memory_intelligence",
            description="Allows the Planner to explicitly save and retrieve semantic knowledge and raw episodes (Rule 15).",
            parameters=[
                CapabilityParameter("action", "string", "Either 'commit_fact', 'update_fact', or 'retrieve'"),
                CapabilityParameter("query", "string", "Search query for 'retrieve' action", required=False),
                CapabilityParameter("sources", "list", "List of sources for 'retrieve', e.g. ['FACTS', 'EPISODES']", required=False),
                CapabilityParameter("fact_data", "dict", "Data for 'commit_fact' or 'update_fact'", required=False),
                CapabilityParameter("old_fact_id", "string", "Required for 'update_fact'", required=False)
            ]
        )
        
    async def invoke(self, params: dict):
        action = params.get("action")
        
        if action == "retrieve":
            query = params.get("query", "")
            raw_sources = params.get("sources", ["FACTS"])
            sources = []
            for s in raw_sources:
                if s == "FACTS": sources.append(MemorySource.FACTS)
                elif s == "EPISODES": sources.append(MemorySource.EPISODES)
                
            limit = params.get("limit", 5)
            results = await self.runtime.retrieve(query, sources, limit)
            
            return {
                "status": "success",
                "context_type": "MemoryRetrieval",
                "results": [r.__dict__ for r in results]
            }
            
        elif action == "commit_fact":
            data = params.get("fact_data", {})
            if not data.get("source_episode_id"):
                return {"status": "error", "message": "Rule 15: Memory Preserves Provenance. source_episode_id is required."}
                
            from desktop.models.memory import FactSourceType
            fact = Fact(
                type=data.get("type", "PREFERENCE"),
                subject=data.get("subject", ""),
                predicate=data.get("predicate", ""),
                value=data.get("value", ""),
                confidence=data.get("confidence", 1.0),
                source_episode_id=data.get("source_episode_id"),
                source_type=FactSourceType(data.get("source_type", "CONVERSATION"))
            )
            await self.runtime.commit_fact(fact)
            return {"status": "success", "fact_id": fact.id}
            
        elif action == "update_fact":
            old_fact_id = params.get("old_fact_id")
            data = params.get("fact_data", {})
            if not old_fact_id or not data.get("source_episode_id"):
                return {"status": "error", "message": "Missing required fields."}
                
            from desktop.models.memory import FactSourceType
            new_fact = Fact(
                type=data.get("type", "PREFERENCE"),
                subject=data.get("subject", ""),
                predicate=data.get("predicate", ""),
                value=data.get("value", ""),
                confidence=data.get("confidence", 1.0),
                source_episode_id=data.get("source_episode_id"),
                source_type=FactSourceType(data.get("source_type", "CONVERSATION"))
            )
            await self.runtime.update_fact(old_fact_id, new_fact)
            return {"status": "success", "superseded_fact": old_fact_id, "new_fact_id": new_fact.id}
            
        elif action == "archive_fact":
            fact_id = params.get("fact_id")
            if not fact_id:
                return {"status": "error", "message": "fact_id is required."}
            await self.runtime.archive_fact(fact_id)
            return {"status": "success"}
            
        return {"status": "error", "message": "Unknown action."}
