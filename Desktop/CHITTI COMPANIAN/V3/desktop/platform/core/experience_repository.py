import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ExperienceRepository:
    """
    Passive storage abstraction for CHITTI's Experience Learning Engine.
    Adheres strictly to storing, loading, searching, and updating workflows.
    Does NOT execute logic or perform lifecycle promotions.
    """
    def __init__(self, storage_path: str = "experience_store.json"):
        self.storage_path = storage_path
        self._experiences: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._experiences = data.get("experiences", {})
            except Exception as e:
                logger.error(f"Failed to load experience store: {e}")
                self._experiences = {}

    def _save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({"experiences": self._experiences}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save experience store: {e}")

    def get_experience(self, exp_id: str) -> Optional[dict]:
        return self._experiences.get(exp_id)

    def save_experience(self, experience: dict) -> str:
        if "id" not in experience:
            experience["id"] = f"exp_{uuid.uuid4().hex[:8]}"
        
        self._experiences[experience["id"]] = experience
        self._save()
        return experience["id"]
        
    def find_best_candidate(self, trigger_transcript: str) -> Optional[dict]:
        """ Finds an existing candidate experience to update its stats """
        normalized = trigger_transcript.lower().strip()
        for exp_id, exp in self._experiences.items():
            if exp.get("status") == "candidate":
                if normalized in [t.lower().strip() for t in exp.get("triggers", [])]:
                    return exp
        return None

    def find_best_match(self, transcript: str, min_confidence: float = 0.8) -> Optional[dict]:
        """
        V1 Fuzzy matching.
        Looks for experiences that are 'stable' and have high confidence.
        """
        normalized_transcript = transcript.lower().strip()
        import string
        normalized_transcript = normalized_transcript.translate(str.maketrans('', '', string.punctuation))
        
        best_match = None
        highest_score = 0.0
        
        for exp_id, exp in self._experiences.items():
            if exp.get("status") != "stable":
                continue
                
            stats = exp.get("statistics", {})
            if stats.get("confidence", 0.0) < min_confidence:
                continue
                
            triggers = exp.get("triggers", [])
            for trigger in triggers:
                norm_trigger = trigger.lower().strip().translate(str.maketrans('', '', string.punctuation))
                
                # Simple exact match or substring match for V1
                if norm_trigger == normalized_transcript:
                    score = 1.0
                elif norm_trigger in normalized_transcript or normalized_transcript in norm_trigger:
                    score = 0.9
                else:
                    score = 0.0
                    
                if score > highest_score:
                    highest_score = score
                    best_match = exp
                    
        return best_match
