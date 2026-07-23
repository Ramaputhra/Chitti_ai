from desktop.brain.intelligence.models import ExplainabilityTrace

class ExplainabilityService:
    def resolve_trace(self, artifact_runtime, graph_runtime, artifact_ids: list) -> ExplainabilityTrace:
        # Resolves artifact IDs back to root MemoryEpisodes
        root_episodes = []
        for aid in artifact_ids:
            if hasattr(artifact_runtime, "artifacts") and aid in artifact_runtime.artifacts:
                art = artifact_runtime.artifacts[aid]
                if hasattr(art, "source_episode_ids"):
                    root_episodes.extend(art.source_episode_ids)
        return ExplainabilityTrace(
            contributing_artifacts=artifact_ids,
            topological_paths=["graph_edge_ref_1"],
            root_episodes=list(set(root_episodes))
        )
