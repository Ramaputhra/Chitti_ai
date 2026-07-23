import psutil
import os
from typing import Optional, Dict, Any

class VSCodeObserver:
    """Detects running VS Code instances and extracts workspace path/project name."""
    
    def observe(self) -> Optional[Dict[str, Any]]:
        try:
            for proc in psutil.process_iter(['name', 'cmdline', 'cwd']):
                if proc.info['name'] and 'Code.exe' in proc.info['name'] or 'code' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline')
                    if cmdline:
                        # Look for folder-uri or simply a path argument
                        for arg in cmdline:
                            if '--folder-uri' in arg:
                                path = arg.split('file://')[-1].strip()
                                return {
                                    "workspace_path": path,
                                    "project_name": os.path.basename(path),
                                    "application": "VS Code"
                                }
                            elif os.path.isdir(arg) and not arg.startswith('--'):
                                return {
                                    "workspace_path": arg,
                                    "project_name": os.path.basename(arg),
                                    "application": "VS Code"
                                }
        except Exception:
            pass
        return None
