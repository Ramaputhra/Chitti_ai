from typing import Tuple, Optional
from desktop.intent.registry import LocalIntentRegistry

class IntentMatcher:
    def __init__(self, registry: LocalIntentRegistry):
        self.registry = registry
        
    def match(self, canonical_text: str) -> Tuple[Optional[str], float]:
        """
        Attempts to match normalized text to an intent ID using aliases.
        Resolves ties using Intent Priority.
        Returns (intent_id, confidence)
        """
        best_match = None
        highest_score = 0.0
        best_priority = -1
        
        for intent_id, definition in self.registry.intent_defs.items():
            for alias in definition.aliases:
                if alias in canonical_text:
                    if alias == canonical_text:
                        score = 1.0
                    else:
                        score = len(alias) / len(canonical_text)
                        
                    # Prioritize exact score. On tie, use definition priority.
                    if score > highest_score or (score == highest_score and definition.priority > best_priority):
                        highest_score = score
                        best_match = intent_id
                        best_priority = definition.priority
                            
        if best_match:
            return best_match, highest_score
            
        return None, 0.0
