import uuid
from typing import Dict, List, Optional
from desktop.productivity.providers.base import ContextProvider, ProviderCapabilities
from desktop.models.session import WorkSession
from desktop.models.evidence import ProviderEvidence, EvidenceSource, EvidenceCluster, RedundantEvidence, EvidenceDomain
from desktop.productivity.workspace_extractor import WorkspaceResolver
from desktop.productivity.command_resolver import CommandResolver

class TerminalProvider(ContextProvider):
    """
    Extracts action-based context from Terminal executions (Rule 46 & 47).
    Groups commands into Workspaces and Command Categories for clean cognition.
    Restoration strictly reconstructs environment state (Rule 48).
    """
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_realtime=True,
            supports_history=False,
            supports_restore=True, # Restores CWD/Shell only (Rule 48)
            supports_statistics=True,
            supports_background_processing=True
        )
        
    @property
    def domain(self) -> EvidenceDomain:
        return EvidenceDomain.ACTION

    @property
    def name(self) -> str:
        return "terminal"
        
    def build_evidence(self, session: WorkSession) -> ProviderEvidence:
        if not session.terminal_events:
            return ProviderEvidence()
            
        cluster_map: Dict[str, EvidenceCluster] = {}
        redundancy_map: Dict[str, RedundantEvidence] = {}
        
        total_failures = 0
        max_duration = 0.0
        unique_commands = set()
        workspaces_visited = set()
        categories_seen = set()
        
        ws_resolver = WorkspaceResolver()
        cmd_resolver = CommandResolver()
        
        for event in session.terminal_events:
            workspace_id = ws_resolver.resolve(event.cwd)
            # Fallback if unresolvable
            ws_root = workspace_id.root if workspace_id else "Unknown"
            ws_name = workspace_id.workspace if workspace_id else event.cwd
            
            cmd_identity = cmd_resolver.resolve(event.command)
            
            # Stats
            if event.exit_code != 0:
                total_failures += 1
            if event.duration_sec > max_duration:
                max_duration = event.duration_sec
                
            unique_commands.add(cmd_identity.identity)
            workspaces_visited.add(ws_name)
            categories_seen.add(cmd_identity.category)
            
            source = EvidenceSource(
                source_id=f"term_{uuid.uuid4().hex[:8]}",
                provider=self.name,
                timestamp=event.timestamp,
                confidence=1.0,
                raw_reference={
                    "command": cmd_identity.metadata.get("raw", event.command),
                    "args": cmd_identity.metadata.get("args", []),
                    "shell": event.shell,
                    "duration": event.duration_sec,
                    "exit_code": event.exit_code,
                    "workspace": ws_name,
                    "category": cmd_identity.category
                }
            )
            
            # 1. RedundantEvidence (Identical Command Identity in same Workspace)
            redundancy_key = f"{ws_name}_{cmd_identity.display_name}"
            if redundancy_key not in redundancy_map:
                redundancy_map[redundancy_key] = RedundantEvidence(
                    label=f"Command: {cmd_identity.display_name}",
                    count=0,
                    sources=[]
                )
                
            red_group = redundancy_map[redundancy_key]
            red_group.count += 1
            red_group.sources.append(source)
            
            # 2. EvidenceCluster (Workspace -> Command Category)
            cluster_key = f"{ws_name}_{cmd_identity.category}"
            if cluster_key not in cluster_map:
                cluster_map[cluster_key] = EvidenceCluster(
                    label=f"Workspace: {ws_name} - Category: {cmd_identity.category}",
                    identity=workspace_id or UnknownIdentity(
                        id=f"ws_{uuid.uuid5(uuid.NAMESPACE_URL, event.cwd).hex[:8]}",
                        type="UNKNOWN",
                        display_name=event.cwd,
                        canonical_path=event.cwd
                    ),
                    duration=0.0,
                    sources=[]
                )
                
            cluster = cluster_map[cluster_key]
            cluster.duration += event.duration_sec
            cluster.sources.append(source)
            
        actual_redundancies = [group for group in redundancy_map.values() if group.count > 1]
        
        return ProviderEvidence(
            clusters=list(cluster_map.values()),
            redundancies=actual_redundancies,
            statistics={
                "commands_executed": len(session.terminal_events),
                "unique_commands": len(unique_commands),
                "repeated_commands": sum(g.count - 1 for g in actual_redundancies),
                "failures": total_failures,
                "longest_running_command_sec": max_duration,
                "distinct_workspaces": len(workspaces_visited),
                "command_categories": len(categories_seen)
            },
            metadata={}
        )
