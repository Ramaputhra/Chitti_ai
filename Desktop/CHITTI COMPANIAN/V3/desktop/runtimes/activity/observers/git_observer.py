import os
from typing import Optional, Dict, Any

class GitObserver:
    """Extracts basic Git state if the workspace is a repository."""
    
    def observe(self, workspace_path: str) -> Optional[Dict[str, Any]]:
        if not workspace_path or not os.path.isdir(os.path.join(workspace_path, '.git')):
            return None
            
        try:
            head_path = os.path.join(workspace_path, '.git', 'HEAD')
            if os.path.exists(head_path):
                with open(head_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content.startswith('ref: refs/heads/'):
                        branch = content.split('/')[-1]
                        return {"git_branch": branch}
        except Exception:
            pass
            
        return {"git_branch": "unknown"}
