import uuid
from typing import List
from datetime import datetime
from desktop.models.analysis import KnowledgeAnalysisTask, AnalysisType, AnalysisStatus

class AnalysisScheduler:
    """
    Listens for KnowledgeUpdated events and schedules asynchronous analysis tasks
    such as Conflict Detection, Consensus, and Trust.
    """
    
    def __init__(self):
        self.task_queue: List[KnowledgeAnalysisTask] = []
        
    def handle_knowledge_updated(self, identity_uuid: str, identity_version: int):
        """
        Triggered when a KnowledgeIdentity's evidence is updated.
        Schedules necessary analysis jobs.
        """
        # Always schedule conflict detection first when evidence changes
        conflict_task = KnowledgeAnalysisTask(
            task_id=str(uuid.uuid4()),
            identity_uuid=identity_uuid,
            analysis_type=AnalysisType.CONFLICT,
            priority=1,
            status=AnalysisStatus.PENDING,
            requested_at=datetime.now(),
            identity_version=identity_version
        )
        self.task_queue.append(conflict_task)
        
        # Future: Schedule Consensus, Trust, etc. 
        # (Could also be chained by the analyzers themselves upon completion)
        
    def get_pending_tasks(self, analysis_type: AnalysisType = None) -> List[KnowledgeAnalysisTask]:
        return [
            t for t in self.task_queue 
            if t.status == AnalysisStatus.PENDING 
            and (analysis_type is None or t.analysis_type == analysis_type)
        ]
