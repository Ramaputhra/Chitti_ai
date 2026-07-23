from typing import List
from desktop.models.session import WorkSession
from desktop.models.evidence import EpisodeSection
from desktop.productivity.providers.registry import ContextProviderRegistry
from desktop.productivity.importance_evaluator import ImportanceEvaluator

class EpisodeBuilder:
    """
    Sole component responsible for constructing provider-agnostic WORK_SESSION episodes.
    Rule 42: Providers must not write directly to memory.
    """
    
    def build_episode(self, session: WorkSession) -> dict:
        """
        Loops over all registered providers, collects ProviderEvidence,
        evaluates importance, and constructs the final episode payload.
        """
        session_duration = session.statistics.duration_sec
        
        # 1. Collect all ProviderEvidence
        all_domain_clusters = []
        redundancies = []
        provider_statistics = {}
        
        for provider in ContextProviderRegistry.providers():
            evidence = provider.build_evidence(session)
            
            if evidence.clusters:
                # Rule 43: Shared evaluation logic
                ImportanceEvaluator.evaluate_clusters(evidence.clusters, session_duration)
                
            for cluster in evidence.clusters:
                all_domain_clusters.append((provider.domain, cluster))
                
            redundancies.extend(evidence.redundancies)
            provider_statistics[provider.name] = evidence.statistics
            
        # 2. Aggregate by Identity (Rule 51)
        from desktop.productivity.identity_aggregator import IdentityAggregator
        from desktop.models.identity import ProjectIdentity, UnknownIdentity
        
        synthesized_evidence = IdentityAggregator.aggregate(all_domain_clusters)
        
        # 3. Sort identities by synthesized importance
        synthesized_evidence.sort(key=lambda e: e.importance_score, reverse=True)
        
        # 4. Hierarchical Grouping
        projects = []
        general_session = []
        
        for ev in synthesized_evidence:
            ev_payload = {
                "identity": ev.identity.display_name,
                "type": ev.identity.type,
                "importance": ev.importance_score,
                "duration": ev.duration,
                "domains": {}
            }
            
            for domain, clusters in ev.clusters_by_domain.items():
                ev_payload["domains"][domain.value] = [
                    {
                        "label": c.label,
                        "importance": c.importance_score,
                        "duration": c.duration,
                        "sources": [
                            {
                                "id": s.source_id,
                                "provider": s.provider,
                                "timestamp": s.timestamp,
                                "raw_reference": s.raw_reference
                            } for s in c.sources
                        ]
                    } for c in clusters
                ]
                
            if isinstance(ev.identity, ProjectIdentity):
                projects.append(ev_payload)
            else:
                general_session.append(ev_payload)
                
        # Construct the final episode payload for MemoryRuntime
        episode_data = {
            "session_id": session.id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "primary_project": session.primary_project,
            "intent": session.intent,
            "statistics": {
                "duration_sec": session_duration,
                "application_count": session.statistics.application_count,
                "document_count": session.statistics.document_count,
                "provider_statistics": provider_statistics
            },
            "hierarchy": {
                "projects": projects,
                "general_session": general_session
            },
            "redundancies": [
                {
                    "label": r.label,
                    "count": r.count
                } for r in redundancies
            ]
        }
        
        return episode_data
