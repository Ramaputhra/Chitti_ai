from typing import List
from desktop.models.workflow import ProjectAssessment, OutcomeType, EvidenceStrength
from desktop.models.intent import IntentType, IntentCategory, IntentEvidence, IntentCandidate

class IntentExtractor:
    """
    Rule 54: Evidence-Driven Intent Modeling.
    Evaluates a ProjectAssessment and proposes deterministic intent candidates 
    without deciding on a primary intent.
    """
    
    @staticmethod
    def extract(assessment: ProjectAssessment) -> List[IntentCandidate]:
        candidates = []
        outcomes = assessment.outcomes
        
        if not outcomes:
            return candidates
            
        # Extract candidates based on outcomes
        for outcome in outcomes:
            # Rule 1: BUILD_FIXED -> FIX_BUILD
            if outcome.type == OutcomeType.BUILD_FIXED:
                candidates.append(IntentCandidate(
                    intent_type=IntentType.FIX_BUILD,
                    category=IntentCategory.DEBUGGING,
                    strength=EvidenceStrength.HIGH,
                    evidence=IntentEvidence(
                        supporting_outcomes=[outcome],
                        trigger_rules=["BUILD_FIXED_OUTCOME_OBSERVED"]
                    )
                ))
            
            # Rule 2: RESEARCH_DOMINANT -> RESEARCH_TOPIC
            elif outcome.type == OutcomeType.RESEARCH_DOMINANT:
                candidates.append(IntentCandidate(
                    intent_type=IntentType.RESEARCH_TOPIC,
                    category=IntentCategory.RESEARCH,
                    strength=EvidenceStrength.HIGH,
                    evidence=IntentEvidence(
                        supporting_outcomes=[outcome],
                        trigger_rules=["RESEARCH_DOMINANT_OUTCOME_OBSERVED"]
                    )
                ))
                
            # Rule 3: VALIDATION_PENDING or IMPLEMENTATION_INTERRUPTED -> IMPLEMENT_FEATURE
            elif outcome.type in (OutcomeType.VALIDATION_PENDING, OutcomeType.IMPLEMENTATION_INTERRUPTED):
                candidates.append(IntentCandidate(
                    intent_type=IntentType.IMPLEMENT_FEATURE,
                    category=IntentCategory.IMPLEMENTATION,
                    strength=EvidenceStrength.MEDIUM,
                    evidence=IntentEvidence(
                        supporting_outcomes=[outcome],
                        trigger_rules=[f"{outcome.type.value}_OUTCOME_OBSERVED"]
                    )
                ))
                
            # Rule 4: TESTS_FAILING -> DEBUG_TESTS
            elif outcome.type == OutcomeType.TESTS_FAILING:
                candidates.append(IntentCandidate(
                    intent_type=IntentType.DEBUG_TESTS,
                    category=IntentCategory.DEBUGGING,
                    strength=EvidenceStrength.HIGH,
                    evidence=IntentEvidence(
                        supporting_outcomes=[outcome],
                        trigger_rules=["TESTS_FAILING_OUTCOME_OBSERVED"]
                    )
                ))
                
            # Rule 5: TESTS_PASSING -> VALIDATE_CHANGES
            elif outcome.type == OutcomeType.TESTS_PASSING:
                candidates.append(IntentCandidate(
                    intent_type=IntentType.VALIDATE_CHANGES,
                    category=IntentCategory.VALIDATION,
                    strength=EvidenceStrength.HIGH,
                    evidence=IntentEvidence(
                        supporting_outcomes=[outcome],
                        trigger_rules=["TESTS_PASSING_OUTCOME_OBSERVED"]
                    )
                ))
                
        return candidates
