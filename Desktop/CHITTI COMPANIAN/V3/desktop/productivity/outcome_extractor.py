from typing import List
from desktop.models.workflow import (
    ProjectWorkflow, ProjectAssessment, WorkflowOutcome, 
    OutcomeType, EvidenceStrength, WorkflowStage, WorkflowAction
)

class OutcomeExtractor:
    """
    Rule 53: Deterministic Outcome Assessment.
    Evaluates a ProjectWorkflow and extracts factual outcomes without inferring intent.
    """
    
    @staticmethod
    def assess(workflow: ProjectWorkflow) -> ProjectAssessment:
        outcomes = []
        events = workflow.events
        
        if not events:
            return ProjectAssessment(workflow=workflow, outcomes=outcomes)
            
        # Extract Test Outcomes
        test_outcomes = OutcomeExtractor._evaluate_tests(events)
        outcomes.extend(test_outcomes)
        
        # Extract Build Outcomes
        build_outcomes = OutcomeExtractor._evaluate_builds(events)
        outcomes.extend(build_outcomes)
        
        # Extract Interruption/Validation State
        interruption_outcomes = OutcomeExtractor._evaluate_interruptions(events)
        outcomes.extend(interruption_outcomes)
        
        # Extract Research Dominance
        if workflow.statistics:
            research_outcome = OutcomeExtractor._evaluate_research(workflow)
            if research_outcome:
                outcomes.append(research_outcome)
                
        return ProjectAssessment(workflow=workflow, outcomes=outcomes)
        
    @staticmethod
    def _evaluate_tests(events: List) -> List[WorkflowOutcome]:
        outcomes = []
        # Find the last test event
        test_events = [e for e in events if e.stage == WorkflowStage.TEST]
        if not test_events:
            return outcomes
            
        last_test = test_events[-1]
        exit_code = last_test.metadata.get("exit_code", -1)
        
        if exit_code == 0:
            outcomes.append(WorkflowOutcome(
                type=OutcomeType.TESTS_PASSING,
                description="Test suite is passing",
                strength=EvidenceStrength.DETERMINISTIC,
                supporting_events=[last_test]
            ))
        else:
            outcomes.append(WorkflowOutcome(
                type=OutcomeType.TESTS_FAILING,
                description="Test suite is failing",
                strength=EvidenceStrength.DETERMINISTIC,
                supporting_events=[last_test]
            ))
            
        return outcomes
        
    @staticmethod
    def _evaluate_builds(events: List) -> List[WorkflowOutcome]:
        outcomes = []
        build_events = [e for e in events if e.stage == WorkflowStage.BUILD]
        if not build_events:
            return outcomes
            
        last_build = build_events[-1]
        exit_code = last_build.metadata.get("exit_code", -1)
        
        if exit_code != 0:
            outcomes.append(WorkflowOutcome(
                type=OutcomeType.BUILD_FAILED,
                description="Build failed",
                strength=EvidenceStrength.DETERMINISTIC,
                supporting_events=[last_build]
            ))
        else:
            # Check if there was a previous failed build
            failed_builds = [e for e in build_events if e.metadata.get("exit_code", 0) != 0]
            if failed_builds:
                # Build Fixed
                outcomes.append(WorkflowOutcome(
                    type=OutcomeType.BUILD_FIXED,
                    description="Build fixed after previous failure",
                    strength=EvidenceStrength.HIGH,
                    supporting_events=[failed_builds[-1], last_build]
                ))
                
        return outcomes
        
    @staticmethod
    def _evaluate_interruptions(events: List) -> List[WorkflowOutcome]:
        outcomes = []
        
        if not events:
            return outcomes
            
        # Determine if the last sequence of events was IMPLEMENTATION
        # without any subsequent BUILD, TEST, or completion signals (like git commit).
        
        last_event = events[-1]
        
        # Check for completion signals in the last few events
        completion_signals = [
            e for e in events[-3:] 
            if e.action == WorkflowAction.RUN_COMMAND and "commit" in str(e.metadata.get("command", "")).lower()
        ]
        
        if completion_signals:
            return outcomes # They completed a task by committing
            
        # Did it end with implementation?
        if last_event.stage == WorkflowStage.IMPLEMENTATION:
            # Did they build or test recently?
            recent_validations = [e for e in events[-5:] if e.stage in (WorkflowStage.TEST, WorkflowStage.BUILD)]
            
            if not recent_validations:
                # Implementation with no validation -> Validation Pending
                outcomes.append(WorkflowOutcome(
                    type=OutcomeType.VALIDATION_PENDING,
                    description="Implementation completed but unvalidated",
                    strength=EvidenceStrength.HIGH,
                    supporting_events=[last_event]
                ))
            else:
                # If they did validate, but ended up back in implementation -> Interrupted
                outcomes.append(WorkflowOutcome(
                    type=OutcomeType.IMPLEMENTATION_INTERRUPTED,
                    description="Implementation interrupted before completion",
                    strength=EvidenceStrength.MEDIUM,
                    supporting_events=events[-2:]
                ))
                
        return outcomes
        
    @staticmethod
    def _evaluate_research(workflow: ProjectWorkflow) -> WorkflowOutcome:
        stats = workflow.statistics
        total_active_time = stats.research_time_sec + stats.coding_time_sec + stats.testing_time_sec + stats.debug_time_sec
        
        if total_active_time > 0 and (stats.research_time_sec / total_active_time) > 0.8:
            return WorkflowOutcome(
                type=OutcomeType.RESEARCH_DOMINANT,
                description="Session was heavily dominated by research",
                strength=EvidenceStrength.HIGH,
                supporting_events=[e for e in workflow.events if e.stage == WorkflowStage.RESEARCH][:3] # attach a few samples
            )
            
        return None
