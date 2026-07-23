from typing import List, Dict, Tuple
from desktop.models.evidence import EvidenceCluster, IdentityEvidence, ProjectEvidence, EvidenceDomain
from desktop.models.identity import Identity, UnknownIdentity, ProjectIdentity

class IdentityAggregator:
    """
    Groups EvidenceClusters by canonical identity across all providers (Rule 51).
    Computes synthesized importance based on provider diversity and duration.
    """
    
    @staticmethod
    def aggregate(domain_clusters: List[Tuple[EvidenceDomain, EvidenceCluster]]) -> List[IdentityEvidence]:
        # Group by canonical path
        # Fallback for UnknownIdentity is their unique ID so they don't merge incorrectly unless identical
        grouped: Dict[str, List[Tuple[EvidenceDomain, EvidenceCluster]]] = {}
        
        for domain, cluster in domain_clusters:
            key = cluster.identity.canonical_path if not isinstance(cluster.identity, UnknownIdentity) else cluster.identity.id
            if key not in grouped:
                grouped[key] = []
            grouped[key].append((domain, cluster))
            
        synthesized_evidence: List[IdentityEvidence] = []
        
        for key, clusters in grouped.items():
            # Find the best identity representation
            # If any is ProjectIdentity, we'll create ProjectEvidence
            identities = [c.identity for _, c in clusters]
            best_identity = identities[0]
            is_project = False
            for idt in identities:
                if isinstance(idt, ProjectIdentity):
                    best_identity = idt
                    is_project = True
                    break
                elif not isinstance(idt, UnknownIdentity) and isinstance(best_identity, UnknownIdentity):
                    best_identity = idt
                    
            evidence_class = ProjectEvidence if is_project else IdentityEvidence
            
            # Group clusters by domain
            clusters_by_domain: Dict[EvidenceDomain, List[EvidenceCluster]] = {}
            total_duration = 0.0
            
            for domain, cluster in clusters:
                if domain not in clusters_by_domain:
                    clusters_by_domain[domain] = []
                clusters_by_domain[domain].append(cluster)
                total_duration += cluster.duration
                
            # Synthesize importance
            # Average importance * (1.0 + 0.1 * (provider_diversity - 1))
            total_importance = sum(c.importance_score for _, c in clusters)
            avg_importance = total_importance / len(clusters) if clusters else 0.0
            provider_diversity = len(set(domain for domain, _ in clusters))
            
            synthesized_score = avg_importance * (1.0 + (0.1 * (provider_diversity - 1)))
            synthesized_score = min(1.0, synthesized_score)
            
            evidence = evidence_class(
                identity=best_identity,
                importance_score=synthesized_score,
                duration=total_duration,
                clusters_by_domain=clusters_by_domain
            )
            synthesized_evidence.append(evidence)
            
        return synthesized_evidence
