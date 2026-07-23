import re
from typing import Optional, Dict
from desktop.models.identity import WorkspaceIdentity, Resolver
import uuid

class WorkspaceResolver(Resolver[str, WorkspaceIdentity]):
    """
    Identifies logical workspaces from raw window titles and paths.
    """
    
    SYSTEM_DIRECTORIES = [
        r"^C:\\Windows",
        r"^C:\\Program Files",
        r"^C:\\Program Files \(x86\)",
        r"^Recycle Bin",
        r"^Control Panel",
        r"^Network",
        r"^This PC",
        r"^Quick Access"
    ]
    
    @staticmethod
    def is_system_noise(path_or_title: str) -> bool:
        for pattern in WorkspaceResolver.SYSTEM_DIRECTORIES:
            if re.match(pattern, path_or_title, re.IGNORECASE):
                return True
        return False
        
    def resolve(self, path: str) -> Optional[WorkspaceIdentity]:
        if not path or WorkspaceResolver.is_system_noise(path):
            return None
            
        # Very simple MVP resolution
        # D:\Projects\CHITTI\src\main.py -> root="D:", workspace="Projects", relative="CHITTI\src\main.py"
        # Since we want "CHITTI" as the workspace:
        # If it's a typical structure: Drive:\Folder\WorkspaceName\...
        
        parts = path.replace('/', '\\').split('\\')
        if len(parts) >= 3 and re.match(r"^[A-Z]:$", parts[0], re.IGNORECASE):
            root = parts[0]
            
            def make_identity(ws: str, rel: str) -> WorkspaceIdentity:
                cp = f"{root}\\{ws}\\{rel}" if rel else f"{root}\\{ws}"
                return WorkspaceIdentity(
                    id=f"ws_{uuid.uuid5(uuid.NAMESPACE_URL, cp).hex[:8]}",
                    type="WORKSPACE",
                    display_name=ws,
                    canonical_path=cp,
                    root=root,
                    workspace=ws,
                    relative_path=rel
                )
            
            if "Users" in parts and "Documents" in parts:
                doc_idx = parts.index("Documents")
                if len(parts) > doc_idx + 1:
                    workspace = parts[doc_idx + 1]
                    rel = "\\".join(parts[doc_idx + 2:])
                    return make_identity(workspace, rel)
                else:
                    return make_identity("Personal Documents", "")
            
            # Default fallback for D:\Projects\CHITTI
            category = parts[1]
            workspace = parts[2] if len(parts) > 2 else category
            rel = "\\".join(parts[3:]) if len(parts) > 3 else ""
            
            # If the path is just D:\Projects, workspace is Projects
            if len(parts) == 2:
                return make_identity(category, "")
                
            return make_identity(workspace, rel)
            
        cp_fallback = path
        return WorkspaceIdentity(
            id=f"ws_{uuid.uuid5(uuid.NAMESPACE_URL, cp_fallback).hex[:8]}",
            type="WORKSPACE",
            display_name="Unknown",
            canonical_path=cp_fallback,
            root="Unknown",
            workspace="Unknown",
            relative_path=cp_fallback
        )

    @staticmethod
    def extract_document(app_name: str, window_title: str) -> Optional[str]:
        if "Visual Studio Code" in window_title:
            parts = window_title.split(" - ")
            if len(parts) > 0:
                return parts[0]
        elif "Notepad" in window_title:
            parts = window_title.split(" - ")
            if len(parts) > 0:
                return parts[0]
        return None

    @staticmethod
    def extract_browser_tab(app_name: str, window_title: str) -> Optional[str]:
        if app_name.lower() in ["chrome", "msedge", "firefox"]:
            parts = window_title.split(" - ")
            if len(parts) > 1:
                return " - ".join(parts[:-1])
        return None
        
    @staticmethod
    def extract_directory(app_name: str, window_title: str) -> Optional[str]:
        if app_name.lower() == "explorer":
            if WorkspaceResolver.is_system_noise(window_title):
                return None
            if re.match(r"^[A-Z]:\\", window_title, re.IGNORECASE):
                return window_title
        elif app_name.lower() in ["powershell", "cmd", "windows terminal"]:
            if re.search(r"[A-Z]:\\[^\s]+", window_title, re.IGNORECASE):
                match = re.search(r"([A-Z]:\\[^\s]+)", window_title, re.IGNORECASE)
                if match and not WorkspaceResolver.is_system_noise(match.group(1)):
                    return match.group(1)
        return None

    @staticmethod
    def classify_project(window_title: str) -> Dict[str, float]:
        if "CHITTI" in window_title:
            return {"CHITTI_Companion": 0.9}
        if "PCB" in window_title:
            return {"PCB_Design": 0.85}
        return {"Unknown": 0.1}
