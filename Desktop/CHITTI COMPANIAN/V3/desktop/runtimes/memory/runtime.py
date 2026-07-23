from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta
from desktop.models.memory import MemoryEpisode
from desktop.models.activity import ActivityEvent

class MemoryEntityIndex:
    """
    Deterministic index mapping entities to memory episodes.
    No AI reasoning involved.
    """
    def __init__(self):
        # Index mappings: key (workspace, app, etc) -> List[episode_id]
        self.workspace_index: Dict[str, List[str]] = {}
        self.application_index: Dict[str, List[str]] = {}
        self.activity_index: Dict[str, List[str]] = {}
        self.entity_index: Dict[str, List[str]] = {} # Generalized entities (URLs, Repos, Files)

    def index_episode(self, episode: MemoryEpisode):
        ep_id = episode.episode_id
        
        if episode.workspace_hint:
            self.workspace_index.setdefault(episode.workspace_hint, []).append(ep_id)
            
        if episode.activity_type:
            self.activity_index.setdefault(episode.activity_type, []).append(ep_id)
            
        for entity in episode.referenced_entities:
            # We index by entity display or type
            if entity.display:
                self.entity_index.setdefault(entity.display, []).append(ep_id)
            if entity.type == "application" and entity.executable:
                self.application_index.setdefault(entity.executable, []).append(ep_id)

class MemoryRuntime:
    """
    Purely storage-oriented episodic memory system.
    Stores immutable MemoryEpisodes exactly as received.
    """
    def __init__(self):
        self.episode_timeline: List[MemoryEpisode] = []
        self.index = MemoryEntityIndex()

    def on_activity_event(self, event: ActivityEvent, session_id: str):
        """Subscribes to immutable ActivityEvents and converts to MemoryEpisodes."""
        episode = MemoryEpisode(
            episode_id=str(uuid.uuid4()),
            activity_type=event.activity_type,
            start_time=event.start_time,
            end_time=event.end_time,
            duration=event.duration,
            workspace_hint=event.workspace_hint,
            referenced_entities=[], # Entities could be mapped from observations if needed
            source_activity_id=event.activity_id,
            source_session_id=session_id,
            related_observation_ids=event.related_observations,
            confidence=event.confidence
        )
        
        self.episode_timeline.append(episode)
        # Ensure chronological ordering just in case events arrive out of order
        self.episode_timeline.sort(key=lambda ep: ep.start_time)
        
        self.index.index_episode(episode)

    def get_recent(self, limit: int = 20) -> List[MemoryEpisode]:
        """Returns Recent Sessions view over the timeline."""
        return self.episode_timeline[-limit:] if self.episode_timeline else []

    def get_by_workspace(self, workspace_hint: str) -> List[MemoryEpisode]:
        ep_ids = self.index.workspace_index.get(workspace_hint, [])
        return [ep for ep in self.episode_timeline if ep.episode_id in ep_ids]

    def get_by_application(self, executable: str) -> List[MemoryEpisode]:
        ep_ids = self.index.application_index.get(executable, [])
        return [ep for ep in self.episode_timeline if ep.episode_id in ep_ids]

    def get_by_time(self, start: datetime, end: datetime) -> List[MemoryEpisode]:
        return [
            ep for ep in self.episode_timeline 
            if ep.start_time >= start and ep.end_time <= end
        ]

    def get_by_entity(self, entity_display: str) -> List[MemoryEpisode]:
        ep_ids = self.index.entity_index.get(entity_display, [])
        return [ep for ep in self.episode_timeline if ep.episode_id in ep_ids]

    def get_by_activity(self, activity_type: str) -> List[MemoryEpisode]:
        ep_ids = self.index.activity_index.get(activity_type, [])
        return [ep for ep in self.episode_timeline if ep.episode_id in ep_ids]
