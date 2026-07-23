import uuid
import time
from typing import Dict, List, Set, Optional
from desktop.productivity.providers.base import ContextProvider, ProviderCapabilities
from desktop.models.session import WorkSession
from desktop.models.evidence import ProviderEvidence, EvidenceSource, EvidenceCluster, RedundantEvidence, EvidenceDomain
from desktop.productivity.workspace_extractor import WorkspaceResolver
from desktop.models.identity import UnknownIdentity

class ExplorerProvider(ContextProvider):
    """
    Extracts Explorer and Terminal context by analyzing active windows and directories (Rule 42).
    """
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_realtime=True,
            supports_history=False,
            supports_restore=True,
            supports_statistics=True,
            supports_background_processing=True
        )
        
    @property
    def domain(self) -> EvidenceDomain:
        return EvidenceDomain.ARTIFACT
        
    @property
    def name(self) -> str:
        return "explorer"
        
    def build_evidence(self, session: WorkSession) -> ProviderEvidence:
        if not session.active_windows:
            return ProviderEvidence()
            
        cluster_map: Dict[str, EvidenceCluster] = {}
        redundancy_map: Dict[str, RedundantEvidence] = {}
        unique_folders = set()
        total_focus_time = 0.0
        drives_visited = set()
        
        # Calculate durations for active windows
        # active_windows is a list of (timestamp, app, title)
        ws_resolver = WorkspaceResolver()
        for i in range(len(session.active_windows)):
            ts, app, title = session.active_windows[i]
            if app.lower() not in ["explorer", "powershell", "cmd", "windows terminal"]:
                continue
                
            path = WorkspaceResolver.extract_directory(app, title)
            if not path:
                continue
                
            workspace_id = ws_resolver.resolve(path)
            if not workspace_id:
                continue
                
            # Duration Calculation
            next_ts = session.active_windows[i+1][0] if i + 1 < len(session.active_windows) else (session.end_time or time.time())
            duration = next_ts - ts
            
            # Avoid noise (< 1 second focus doesn't mean much)
            if duration < 1.0:
                continue
                
            total_focus_time += duration
            unique_folders.add(path)
            drives_visited.add(workspace_id.root)
            
            source = EvidenceSource(
                source_id=f"expl_{uuid.uuid4().hex[:8]}",
                provider=self.name,
                timestamp=ts,
                confidence=1.0,
                raw_reference={
                    "path": path,
                    "workspace": workspace_id.workspace,
                    "duration": duration,
                    "exists": True # Minimal mock metadata
                }
            )
            
            # 1. RedundantEvidence (Repeated visits to exact same folder)
            if path not in redundancy_map:
                redundancy_map[path] = RedundantEvidence(
                    label=f"Folder: {path}",
                    count=0,
                    sources=[]
                )
            
            red_group = redundancy_map[path]
            red_group.count += 1
            red_group.sources.append(source)
            
            # 2. EvidenceCluster (Workspace level)
            cluster_key = f"{workspace_id.root}\\{workspace_id.workspace}"
            if cluster_key not in cluster_map:
                cluster_map[cluster_key] = EvidenceCluster(
                    label=f"Workspace: {workspace_id.workspace}",
                    identity=workspace_id,
                    duration=0.0,
                    sources=[]
                )
                
            cluster = cluster_map[cluster_key]
            cluster.duration += duration
            cluster.sources.append(source)
            
        actual_redundancies = [group for group in redundancy_map.values() if group.count > 1]
        
        return ProviderEvidence(
            clusters=list(cluster_map.values()),
            redundancies=actual_redundancies,
            statistics={
                "folders_visited": sum(g.count for g in redundancy_map.values()),
                "unique_folders": len(unique_folders),
                "repeated_visits": sum(g.count - 1 for g in actual_redundancies),
                "focus_time": total_focus_time,
                "distinct_drives": len(drives_visited)
            },
            metadata={}
        )
