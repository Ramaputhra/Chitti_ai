from typing import List, Dict, Any, Tuple
from desktop.models.activity import ActivityMemoryModel

class ActivityResolver:
    """
    Evaluates recent ActivityMemoryModels and scores them to determine
    which activity the user most likely wants to resume.
    """
    
    def __init__(self):
        # In a real implementation, this would query Semantic/Episodic Memory
        pass

    def resolve_activity(self, recent_activities: List[ActivityMemoryModel], user_intent: str) -> Tuple[Optional[ActivityMemoryModel], float, List[Dict[str, Any]]]:
        """
        Returns the selected activity, the confidence score (0.0 to 1.0),
        and the full scored list.
        """
        if not recent_activities:
            return None, 0.0, []
            
        scored_activities = []
        for activity in recent_activities:
            score = self._calculate_confidence(activity, user_intent)
            scored_activities.append({
                "activity": activity,
                "score": score,
                "type": activity.activity_type
            })
            
        # Sort by score descending
        scored_activities.sort(key=lambda x: x["score"], reverse=True)
        
        best_match = scored_activities[0]
        return best_match["activity"], best_match["score"], scored_activities

    def _calculate_confidence(self, activity: ActivityMemoryModel, intent: str) -> float:
        """
        Mock scoring logic. In reality, would use embeddings or heuristics
        comparing the intent ("Continue my React project") with the activity details.
        """
        # Placeholder for complex NLP resolution
        if "react" in intent.lower() and activity.activity_type == "Coding":
            return 0.92
        if "research" in intent.lower() and activity.activity_type == "Research":
            return 0.85
            
        return 0.35 # Low confidence fallback
