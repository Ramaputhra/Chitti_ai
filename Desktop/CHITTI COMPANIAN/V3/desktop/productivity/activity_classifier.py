from desktop.models.session import WorkSession
from typing import Set

class ActivityClassifier:
    """
    Layer 1: Objective Activity Extraction.
    Maps applications and titles to raw activities without reasoning.
    """
    
    @staticmethod
    def extract_activities(session: WorkSession, active_app: str, active_title: str) -> Set[str]:
        activities = set()
        
        # Analyze current snapshot
        apps = session.applications | {active_app}
        tabs = session.browser_tabs
        
        if "Code" in active_app or "VSCode" in active_app:
            activities.add("Editing Code")
            
        if "chrome" in active_app.lower() or "edge" in active_app.lower():
            activities.add("Browsing")
            
        if "terminal" in active_app.lower() or "cmd" in active_app.lower() or "powershell" in active_app.lower():
            activities.add("Terminal")
            
        for tab in tabs:
            if "pdf" in tab.lower():
                activities.add("Reading PDF")
                
        # Simple heuristic, expands over time
        return activities
