from typing import List, Dict, Any, Tuple
from desktop.models.workflow import WorkflowAction, WorkflowStage, WorkflowEvent, WorkflowStatistics, ProjectWorkflow, GeneralWorkflow
from desktop.models.evidence import EvidenceDomain
from desktop.models.identity import Identity, ProjectIdentity, UnknownIdentity

class WorkflowReconstructor:
    """
    Rule 52: Deterministic Workflow Reconstruction.
    Converts aggregated WORK_SESSION hierarchies back into deterministic temporal sequences.
    """
    
    @staticmethod
    def reconstruct(session_data: Dict[str, Any]) -> Tuple[List[ProjectWorkflow], List[GeneralWorkflow]]:
        projects = []
        general = []
        
        hierarchy = session_data.get("hierarchy", {})
        project_payloads = hierarchy.get("projects", [])
        general_payloads = hierarchy.get("general_session", [])
        
        for payload in project_payloads:
            workflow = WorkflowReconstructor._reconstruct_project(payload)
            projects.append(workflow)
            
        for payload in general_payloads:
            workflow = WorkflowReconstructor._reconstruct_general(payload)
            general.append(workflow)
            
        return projects, general
        
    @staticmethod
    def _reconstruct_project(payload: Dict[str, Any]) -> ProjectWorkflow:
        identity = ProjectIdentity(
            id=payload.get("identity", ""),
            display_name=payload.get("identity", ""),
            canonical_path=payload.get("identity", "")
        )
        
        events = WorkflowReconstructor._extract_events(identity, payload.get("domains", {}))
        
        stats = WorkflowReconstructor._calculate_statistics(events)
        status = WorkflowReconstructor._determine_status(events)
        
        return ProjectWorkflow(
            project_identity=identity,
            events=events,
            statistics=stats,
            status=status
        )
        
    @staticmethod
    def _reconstruct_general(payload: Dict[str, Any]) -> GeneralWorkflow:
        identity = UnknownIdentity(
            id=payload.get("identity", ""),
            display_name=payload.get("identity", ""),
            canonical_path=payload.get("identity", "")
        )
        
        events = WorkflowReconstructor._extract_events(identity, payload.get("domains", {}))
        stats = WorkflowReconstructor._calculate_statistics(events)
        
        return GeneralWorkflow(
            events=events,
            statistics=stats
        )

    @staticmethod
    def _extract_events(identity: Identity, domains: Dict[str, List[Dict[str, Any]]]) -> List[WorkflowEvent]:
        events = []
        
        for domain_name, clusters in domains.items():
            try:
                domain_enum = EvidenceDomain(domain_name)
            except ValueError:
                continue
                
            for cluster in clusters:
                sources = cluster.get("sources", [])
                for source in sources:
                    timestamp = source.get("timestamp", 0.0)
                    raw_ref = source.get("raw_reference", {})
                    
                    action, stage = WorkflowReconstructor._map_action_and_stage(domain_name, raw_ref)
                    
                    duration = raw_ref.get("duration", 0.0)
                    start_time = timestamp
                    end_time = timestamp + duration
                    
                    event = WorkflowEvent(
                        identity=identity,
                        domain=domain_enum,
                        action=action,
                        stage=stage,
                        start_time=start_time,
                        end_time=end_time,
                        metadata=raw_ref
                    )
                    events.append(event)
                    
        # Sort chronologically by start_time
        events.sort(key=lambda e: e.start_time)
        return events
        
    @staticmethod
    def _map_action_and_stage(domain: str, raw_reference: dict) -> Tuple[WorkflowAction, WorkflowStage]:
        if domain == "RESEARCH":
            return WorkflowAction.READ_DOCUMENT, WorkflowStage.RESEARCH
        elif domain == "EXTRACTION":
            return WorkflowAction.COPY_TEXT, WorkflowStage.RESEARCH
        elif domain == "ARTIFACT":
            if "workspace" in raw_reference and "duration" in raw_reference and "exists" in raw_reference:
                return WorkflowAction.OPEN_FOLDER, WorkflowStage.IMPLEMENTATION
            else:
                return WorkflowAction.EDIT_FILE, WorkflowStage.IMPLEMENTATION
        elif domain == "ACTION":
            cat = raw_reference.get("category", "")
            action = WorkflowAction.RUN_COMMAND
            stage = WorkflowStage.UNKNOWN
            
            if cat == "TEST":
                stage = WorkflowStage.TEST
            elif cat == "BUILD":
                stage = WorkflowStage.BUILD
            elif cat == "GIT" or cat == "VERSION_CONTROL":
                stage = WorkflowStage.IMPLEMENTATION
            elif cat == "PYTHON" or cat == "NPM" or cat == "RUNTIME":
                stage = WorkflowStage.TEST # Execution is often test/debug
            
            return action, stage
            
        return WorkflowAction.UNKNOWN, WorkflowStage.UNKNOWN

    @staticmethod
    def _calculate_statistics(events: List[WorkflowEvent]) -> WorkflowStatistics:
        stats = WorkflowStatistics()
        
        for event in events:
            duration = event.end_time - event.start_time
            if event.stage == WorkflowStage.RESEARCH:
                stats.research_time_sec += duration
            elif event.stage == WorkflowStage.IMPLEMENTATION:
                stats.coding_time_sec += duration
            elif event.stage == WorkflowStage.TEST:
                stats.testing_time_sec += duration
            elif event.stage == WorkflowStage.DEBUG:
                stats.debug_time_sec += duration
                
            if event.action == WorkflowAction.RUN_COMMAND:
                cat = event.metadata.get("category", "")
                if cat == "BUILD":
                    stats.build_attempts += 1
                    if event.metadata.get("exit_code", 0) != 0:
                        stats.failures += 1
                elif cat == "TEST" or cat == "PYTHON" or cat == "RUNTIME":
                    if event.metadata.get("exit_code", 0) != 0:
                        stats.failures += 1
                        
        return stats

    @staticmethod
    def _determine_status(events: List[WorkflowEvent]) -> str:
        if not events:
            return "Empty"
            
        # Check the last terminal commands to determine outcome
        terminal_events = [e for e in events if e.action == WorkflowAction.RUN_COMMAND]
        if not terminal_events:
            return "In Progress"
            
        last_event = terminal_events[-1]
        exit_code = last_event.metadata.get("exit_code", 0)
        
        if exit_code == 0:
            return "Completed Successfully"
        else:
            return "Ended With Failures"
