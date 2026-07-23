import psutil
from typing import Optional, Dict, Any

class NodeObserver:
    """Detects running Node.js development servers (npm, vite, react-scripts, etc.)."""
    
    def observe(self, workspace_path: str) -> Optional[Dict[str, Any]]:
        if not workspace_path:
            return None
            
        try:
            for proc in psutil.process_iter(['name', 'cmdline', 'cwd']):
                try:
                    name = proc.info.get('name', '').lower()
                    cmdline = proc.info.get('cmdline', [])
                    cwd = proc.info.get('cwd', '')
                    
                    if not cwd or cwd.lower().rstrip('\\/') != workspace_path.lower().rstrip('\\/'):
                        continue
                        
                    is_node = 'node' in name or 'npm' in name
                    has_dev_args = any(arg in ['start', 'dev', 'run'] for arg in cmdline)
                    
                    if is_node and has_dev_args:
                        # Reconstruct command
                        launch_command = " ".join(cmdline) if cmdline else "npm start"
                        
                        # Simplistic port inference for V1.1
                        port = "5173" if "vite" in launch_command else "3000"
                        
                        return {
                            "launch_command": "npm",
                            "readiness": f"port: {port}, expected_status: 200",
                            "browser_url": f"http://localhost:{port}"
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
            
        return None
