import os
import psutil
from typing import Optional
from desktop.models.companion import ActivityMemoryModel, ActivityState

class ActivityValidator:
    """
    Validates a historical ActivityMemoryModel against the current system state
    to determine its resume_confidence and update its ActivityState.
    """
    
    def validate(self, activity: Optional[ActivityMemoryModel]) -> Optional[ActivityMemoryModel]:
        if not activity:
            return None
            
        confidence = 0.0
        
        # 1. Check Workspace Existence
        workspace_path = activity.workspace_path
        if workspace_path and os.path.exists(workspace_path):
            confidence += 0.3
            
            # 2. Check Git Repo
            if os.path.isdir(os.path.join(workspace_path, '.git')):
                confidence += 0.2
        else:
            activity.state = ActivityState.FAILED
            activity.resume_confidence = 0.0
            return activity
            
        # 3. Check VS Code Running State (Heuristic)
        is_vscode_running = False
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and ('Code.exe' in proc.info['name'] or 'code' in proc.info['name'].lower()):
                    is_vscode_running = True
                    break
        except Exception:
            pass
            
        if is_vscode_running:
            confidence += 0.2
            activity.state = ActivityState.ACTIVE
        else:
            activity.state = ActivityState.PAUSED
            
        # 4. Check Dev command executable (Optional heuristic, if npm exists)
        confidence += 0.2  # Assuming npm/node is in PATH for now in V1
        
        # 5. Assign computed confidence
        activity.resume_confidence = confidence
        return activity
