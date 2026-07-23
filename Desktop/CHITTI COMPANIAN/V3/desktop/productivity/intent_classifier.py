from desktop.models.intent import IntentRegistry, TaskProfile
from desktop.models.session import WorkSession
from typing import Tuple

class IntentClassifier:
    """
    Layer 2: Semantic Intent Interpretation.
    Combines objective activities and context to infer high-level intent.
    Rule 38: Observations before Interpretation.
    """
    def __init__(self, registry: IntentRegistry):
        self.registry = registry
        
    def classify(self, session: WorkSession) -> Tuple[str, float, set]:
        best_intent = "Unknown"
        max_score = 0.0
        best_evidence = set()
        
        # Combine all textual evidence
        evidence_text = set()
        for t in session.browser_title_hints:
            evidence_text.update(t.lower().split())
        for d in session.documents:
            evidence_text.update(d.lower().split())
            
        for profile in self.registry.profiles.values():
            score = 0.0
            current_evidence = set()
            
            # Check activities (e.g. Editing Code, Browsing)
            matching_activities = session.activities.intersection(profile.required_activities)
            if matching_activities:
                # Base score from activities
                score += (len(matching_activities) / max(1, len(profile.required_activities))) * 0.5
                current_evidence.update(matching_activities)
                
            # Check keywords
            matching_keywords = evidence_text.intersection(profile.keywords)
            if matching_keywords:
                score += min((len(matching_keywords) / max(1, len(profile.keywords))) * 0.3, 0.3)
                current_evidence.update(matching_keywords)
                
            # Check domains
            matching_domains = False
            for d in profile.domains:
                if any(d in tab.lower() for tab in session.browser_title_hints):
                    matching_domains = True
                    current_evidence.add(d)
                    break
            if matching_domains:
                score += 0.2
                
            if score > max_score:
                max_score = score
                best_intent = profile.name
                best_evidence = current_evidence
                
        # If score is very low, fallback to Unknown
        if max_score < 0.2:
            return ("Unknown", max_score, set())
            
        return (best_intent, max_score, best_evidence)
