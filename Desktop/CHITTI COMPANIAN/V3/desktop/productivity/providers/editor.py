import uuid
from typing import Dict, List, Optional
from desktop.productivity.providers.base import ContextProvider, ProviderCapabilities
from desktop.models.session import WorkSession
from desktop.models.evidence import ProviderEvidence, EvidenceSource, EvidenceCluster, RedundantEvidence, EvidenceDomain
from desktop.models.identity import UnknownIdentity
from desktop.productivity.project_resolver import ProjectResolver
from desktop.productivity.workspace_extractor import WorkspaceResolver

class EditorProvider(ContextProvider):
    """
    Extracts edited files from active windows and groups them by ProjectIdentity.
    Editor-agnostic: tracks VS Code, Visual Studio, IntelliJ, etc.
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
        return "editor"
        
    def build_evidence(self, session: WorkSession) -> ProviderEvidence:
        if not session.active_windows:
            return ProviderEvidence()
            
        cluster_map: Dict[str, EvidenceCluster] = {}
        redundancy_map: Dict[str, RedundantEvidence] = {}
        
        project_resolver = ProjectResolver()
        
        total_focus_time = 0.0
        unique_files = set()
        projects_visited = set()
        
        for i in range(len(session.active_windows)):
            ts, app, title = session.active_windows[i]
            
            # Simple heuristic for common IDEs
            is_editor = any(editor in title for editor in ["Visual Studio Code", "IntelliJ", "PyCharm", "WebStorm"])
            is_editor = is_editor or app.lower() in ["code", "devenv", "idea64", "pycharm", "sublime_text", "notepad++", "cursor"]
            
            if not is_editor:
                continue
                
            # Extract document name (naive for MVP, could use UI automation in future)
            # Typically "main.py - CHITTI - Visual Studio Code"
            doc_name = WorkspaceResolver.extract_document(app, title)
            if not doc_name:
                continue
                
            # To resolve the project, we need a path. 
            # If the title doesn't have full path, we can't reliably resolve project.
            # But wait, active_windows doesn't store full path for editors unless it's in the title.
            # For the MVP, let's assume we can resolve the project if we have the Workspace name from the title
            # OR we mock the path. Let's just try to resolve the title as a path.
            # If it fails, we fall back to a mock ProjectIdentity for now, or just use the extracted Workspace string.
            
            # In a real implementation, we would query the Editor's API or use a more advanced UI inspector.
            # For this MVP, we'll try to extract the workspace from the title (e.g., "CHITTI").
            
            # Since we can't easily get the absolute path of the open file from just the window title in most cases,
            # we'll create a dummy path based on the workspace name if it exists in directories.
            # Let's find a directory in session.directories that matches this title.
            
            possible_path = None
            for d in session.directories:
                if title.find(d.split('\\')[-1]) != -1:
                    possible_path = d
                    break
                    
            if not possible_path and session.directories:
                # Fallback to the first directory if we have one
                possible_path = next(iter(session.directories))
                
            if possible_path:
                project_id = project_resolver.resolve(possible_path)
            else:
                project_id = None
                
            proj_name = project_id.display_name if project_id else "Unknown Project"
            
            # Duration Calculation
            next_ts = session.active_windows[i+1][0] if i + 1 < len(session.active_windows) else session.end_time
            if next_ts is None:
                next_ts = ts + 1.0
            duration = next_ts - ts
            
            if duration < 1.0:
                continue
                
            total_focus_time += duration
            unique_files.add(doc_name)
            projects_visited.add(proj_name)
            
            source = EvidenceSource(
                source_id=f"edit_{uuid.uuid4().hex[:8]}",
                provider=self.name,
                timestamp=ts,
                confidence=0.8,
                raw_reference={
                    "file": doc_name,
                    "project": proj_name,
                    "duration": duration,
                    "editor": app
                }
            )
            
            # Redundant (Same file in same project)
            red_key = f"{proj_name}_{doc_name}"
            if red_key not in redundancy_map:
                redundancy_map[red_key] = RedundantEvidence(
                    label=f"File: {doc_name}",
                    count=0,
                    sources=[]
                )
                
            red_group = redundancy_map[red_key]
            red_group.count += 1
            red_group.sources.append(source)
            
            # Cluster (Project)
            if proj_name not in cluster_map:
                cluster_map[proj_name] = EvidenceCluster(
                    label=f"Project: {proj_name}",
                    identity=project_id or UnknownIdentity(
                        id=f"proj_{uuid.uuid5(uuid.NAMESPACE_URL, proj_name).hex[:8]}",
                        type="UNKNOWN",
                        display_name=proj_name,
                        canonical_path=proj_name
                    ),
                    duration=0.0,
                    sources=[]
                )
                
            cluster = cluster_map[proj_name]
            cluster.duration += duration
            cluster.sources.append(source)
            
        actual_redundancies = [group for group in redundancy_map.values() if group.count > 1]
        
        return ProviderEvidence(
            clusters=list(cluster_map.values()),
            redundancies=actual_redundancies,
            statistics={
                "files_edited": sum(g.count for g in redundancy_map.values()),
                "unique_files": len(unique_files),
                "editor_focus_time_sec": total_focus_time,
                "distinct_projects": len(projects_visited)
            },
            metadata={}
        )
