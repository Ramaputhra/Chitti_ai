import time
from typing import Dict, Any, Optional, Tuple, List
from desktop.models.memory import (
    Episode, EpisodeScore, EpisodeQuality, ReplayStatistics, OptimizationRecommendation
)

class MemoryLearningEngine:
    """
    COG-31F: Learning & Optimization Engine.
    Stateless internal engine composed by MemoryRuntime.
    Evolves EpisodeScore, EpisodeQuality, ReplayStatistics, and evaluates lifecycle transitions
    upon receiving ExecutionCompletedEvent signals.
    """
    def __init__(self, alpha: float = 0.15, beta: float = 0.40, retention_threshold: float = 0.10):
        self.alpha = alpha  # Score boost factor on success
        self.beta = beta    # Score penalty factor on failure
        self.retention_threshold = retention_threshold  # Retention threshold (S < 0.10 -> Removal)

    def evolve_episode_score(self, current_score: float, is_success: bool) -> float:
        """
        Evolves EpisodeScore dynamically.
        Success: S_(t+1) = min(1.0, S_t + alpha * (1.0 - S_t))
        Failure: S_(t+1) = max(0.0, S_t - beta * S_t)
        """
        if is_success:
            new_score = current_score + self.alpha * (1.0 - current_score)
            return min(1.0, max(0.0, round(new_score, 4)))
        else:
            new_score = current_score - self.beta * current_score
            return min(1.0, max(0.0, round(new_score, 4)))

    def evolve_episode_quality(
        self, current_quality: EpisodeQuality, is_success: bool, latency_ms: float
    ) -> EpisodeQuality:
        """
        Evolves EpisodeQuality moving average accuracy confidence and applies latency penalties.
        """
        current_acc = getattr(current_quality, "accuracy_confidence", 1.0) if current_quality else 1.0
        success_val = 1.0 if is_success else 0.0
        
        # Exponential moving average accuracy
        new_acc = 0.80 * current_acc + 0.20 * success_val

        # Latency adjustment (latency > 2000ms applies subtle penalty)
        latency_penalty = max(0.5, 1.0 - (latency_ms / 10000.0)) if latency_ms > 2000 else 1.0
        final_acc = min(1.0, max(0.0, round(new_acc * latency_penalty, 4)))

        version = getattr(current_quality, "version", "1.0") if current_quality else "1.0"
        return EpisodeQuality(
            latency_ms=latency_ms,
            accuracy_confidence=final_acc,
            version=version
        )

    def update_replay_statistics(
        self, stats: Optional[ReplayStatistics], is_success: bool, latency_ms: float
    ) -> ReplayStatistics:
        """
        Updates operational ReplayStatistics metadata.
        """
        now = time.time()
        if not stats:
            stats = ReplayStatistics()

        replay_count = stats.replay_count + 1
        success_count = stats.success_count + (1 if is_success else 0)
        failure_count = stats.failure_count + (0 if is_success else 1)
        
        # Calculate moving average latency
        if stats.replay_count == 0:
            avg_latency = latency_ms
        else:
            avg_latency = (stats.average_latency_ms * stats.replay_count + latency_ms) / replay_count

        last_success = now if is_success else stats.last_success_timestamp

        return ReplayStatistics(
            replay_count=replay_count,
            success_count=success_count,
            failure_count=failure_count,
            average_latency_ms=round(avg_latency, 2),
            last_used_timestamp=now,
            last_success_timestamp=last_success
        )

    def evaluate_lifecycle_and_recommendations(
        self, episode: Episode, new_score: float, stats: ReplayStatistics
    ) -> Tuple[str, List[OptimizationRecommendation]]:
        """
        Evaluates lifecycle transition (ACTIVE, PROMOTED, DECAYED, REMOVE_UNTRUSTED)
        and outputs advisory OptimizationRecommendation objects.
        """
        recommendations = []

        # Check retention threshold (S < 0.10 -> Untrusted Removal)
        if new_score < self.retention_threshold:
            recommendations.append(OptimizationRecommendation(
                recommendation_type="PRUNE_UNTRUSTED_EPISODE",
                target_component="MemoryRuntime",
                observation=f"Episode {episode.episode_id} score {new_score:.4f} dropped below retention threshold {self.retention_threshold}",
                suggested_value={"action": "REMOVE_FROM_COGNITIVE_MEMORY", "episode_id": episode.episode_id},
                confidence=1.0
            ))
            return "REMOVE_UNTRUSTED", recommendations

        # Check Promotion (S >= 0.85 and success_count >= 3)
        if new_score >= 0.85 and stats.success_count >= 3:
            lifecycle_state = "PROMOTED"
        else:
            lifecycle_state = "ACTIVE"

        # Advisory tuning recommendation
        if stats.failure_count > 2 and stats.success_rate < 0.50:
            recommendations.append(OptimizationRecommendation(
                recommendation_type="REDUCE_REPLAY_CONFIDENCE",
                target_component="MemoryRetrievalEngine",
                observation=f"Episode {episode.episode_id} failure rate is {1.0 - stats.success_rate:.2f}",
                suggested_value={"episode_id": episode.episode_id, "decay_boost": 0.20},
                confidence=0.85
            ))

        return lifecycle_state, recommendations

    def process_execution_outcome(
        self, episode: Episode, is_success: bool, latency_ms: float, current_stats: Optional[ReplayStatistics] = None
    ) -> Dict[str, Any]:
        """
        Main processing method called by MemoryRuntime on ExecutionCompletedEvent.
        Evolves metadata without mutating historical Episode content.
        """
        cur_score_val = episode.episode_score.score if episode.episode_score else 0.50
        new_score_val = self.evolve_episode_score(cur_score_val, is_success)

        updated_score = EpisodeScore(
            score=new_score_val,
            last_updated=time.time(),
            decay_factor=getattr(episode.episode_score, "decay_factor", 1.0) if episode.episode_score else 1.0
        )

        updated_quality = self.evolve_episode_quality(episode.episode_quality, is_success, latency_ms)
        updated_stats = self.update_replay_statistics(current_stats, is_success, latency_ms)
        lifecycle_state, recommendations = self.evaluate_lifecycle_and_recommendations(episode, new_score_val, updated_stats)

        return {
            "episode_id": episode.episode_id,
            "updated_score": updated_score,
            "updated_quality": updated_quality,
            "updated_stats": updated_stats,
            "lifecycle_state": lifecycle_state,
            "recommendations": recommendations,
            "should_remove": (lifecycle_state == "REMOVE_UNTRUSTED")
        }
