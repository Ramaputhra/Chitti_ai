from typing import Dict, Any, List
from desktop.runtimes.memory.models import TimelineQuery, Episode
from desktop.runtimes.memory.timeline import ExperienceTimeline

class MemoryRecallCapability:
    """
    Executes a semantic or structured query against the Experience Timeline 
    and synthesizes an answer using the AI Runtime.
    """
    def __init__(self, timeline: ExperienceTimeline, ai_runtime):
        self.timeline = timeline
        self.ai_runtime = ai_runtime

    async def execute(self, payload: Dict[str, Any]) -> str:
        # 1. Parse natural language intent into a TimelineQuery (Stub)
        # We would normally use the AI Runtime here to map "What was I doing yesterday?"
        # into a `TimelineQuery(start_time=yesterday, end_time=today)`.
        
        query = TimelineQuery(
            intent=payload.get("intent_filter")
        )
        
        # 2. Retrieve Episodes (and potentially Sessions/Knowledge in full version)
        episodes = self.timeline.query(query)
        
        # 3. Synthesize the Answer
        if not episodes:
            return "I don't have any records matching that timeframe."
            
        # In reality, pass the episodes to the AI Runtime to generate a fluent summary
        # ai_summary = await self.ai_runtime.invoke_capability("generate", {"episodes": episodes})
        
        project_count = len(set(ep.project for ep in episodes if ep.project))
        return f"You had {len(episodes)} episodes of activity spanning {project_count} projects. Primary intent was '{episodes[0].intent}' in {episodes[0].project}."
