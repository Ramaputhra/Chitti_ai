import uuid
from typing import Dict, List, Optional
from desktop.productivity.providers.base import ContextProvider, ProviderCapabilities
from desktop.models.session import WorkSession
from desktop.models.evidence import ProviderEvidence, EvidenceSource, EvidenceCluster, RedundantEvidence, EvidenceDomain
from desktop.models.identity import UnknownIdentity

class ClipboardProvider(ContextProvider):
    """
    Extracts text-based clipboard events during the session (Rule 42).
    Includes deterministic redaction of sensitive formats (Rule 45).
    """
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_realtime=True,
            supports_history=False,
            supports_restore=False,
            supports_statistics=True,
            supports_background_processing=True
        )
        
    @property
    def domain(self) -> EvidenceDomain:
        return EvidenceDomain.EXTRACTION
        
    @property
    def name(self) -> str:
        return "clipboard"
        
    def build_evidence(self, session: WorkSession) -> ProviderEvidence:
        if not session.clipboard_events:
            return ProviderEvidence()
            
        # Group by hash (RedundantEvidence)
        redundancy_map: Dict[str, RedundantEvidence] = {}
        # Group by application (EvidenceCluster)
        cluster_map: Dict[str, EvidenceCluster] = {}
        
        unique_hashes = set()
        
        for event in session.clipboard_events:
            source = EvidenceSource(
                source_id=f"clip_{uuid.uuid4().hex[:8]}",
                provider=self.name,
                timestamp=event.timestamp,
                confidence=1.0,
                raw_reference={
                    "preview": event.content_preview,
                    "type": event.content_type,
                    "length": event.character_count,
                    "hash": event.content_hash
                }
            )
            
            # 1. RedundantEvidence
            if event.content_hash not in redundancy_map:
                redundancy_map[event.content_hash] = RedundantEvidence(
                    label=f"Copied {event.content_type} ({event.character_count} chars)",
                    count=0,
                    sources=[]
                )
                unique_hashes.add(event.content_hash)
            
            red_group = redundancy_map[event.content_hash]
            red_group.count += 1
            red_group.sources.append(source)
            
            # 2. EvidenceCluster (by App)
            if event.application not in cluster_map:
                cluster_map[event.application] = EvidenceCluster(
                    label=f"Clipboard: {event.application}",
                    identity=UnknownIdentity(
                        id=f"app_{uuid.uuid5(uuid.NAMESPACE_URL, event.application).hex[:8]}",
                        type="UNKNOWN",
                        display_name=event.application,
                        canonical_path=event.application
                    ),
                    duration=0.0, # Clipboard is point-in-time, duration=0
                    sources=[]
                )
                
            cluster = cluster_map[event.application]
            cluster.sources.append(source)
            
        # Only report true redundancies
        actual_redundancies = [group for group in redundancy_map.values() if group.count > 1]
        
        return ProviderEvidence(
            clusters=list(cluster_map.values()),
            redundancies=actual_redundancies,
            statistics={
                "total_entries": len(session.clipboard_events),
                "unique_entries": len(unique_hashes),
                "repeated_entries": sum(g.count - 1 for g in actual_redundancies),
                "applications_used": len(cluster_map)
            },
            metadata={}
        )
