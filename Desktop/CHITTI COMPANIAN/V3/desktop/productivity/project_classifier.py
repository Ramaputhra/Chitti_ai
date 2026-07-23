from typing import Dict, Any, Tuple

class ProjectClassifier:
    """
    Computes a project classification based on weighted evidence.
    """
    
    @staticmethod
    def classify(directories: set, documents: set, browser_tabs: set, window_titles: set) -> Tuple[str, float]:
        scores = {}
        
        # Helper to apply weights
        def add_score(project: str, weight: float):
            scores[project] = scores.get(project, 0.0) + weight
            
        # Example naive weighted mapping for MVP
        for d in directories:
            if "CHITTI" in d:
                add_score("CHITTI_Companion", 5.0)
            elif "PCB" in d:
                add_score("PCB_Design", 5.0)
                
        for doc in documents:
            if "chitti" in doc.lower():
                add_score("CHITTI_Companion", 3.0)
            elif "schematic" in doc.lower():
                add_score("PCB_Design", 3.0)
                
        for tab in browser_tabs:
            if "chitti" in tab.lower():
                add_score("CHITTI_Companion", 2.0)
                
        for t in window_titles:
            if "chitti" in t.lower():
                add_score("CHITTI_Companion", 1.0)
                
        if not scores:
            return ("Unknown", 0.1)
            
        # Normalize (rough normalization for MVP)
        max_possible = 5.0 + 3.0 + 2.0 + 1.0
        best_project = max(scores.items(), key=lambda x: x[1])
        
        confidence = min(best_project[1] / max_possible, 0.99)
        return (best_project[0], confidence)
