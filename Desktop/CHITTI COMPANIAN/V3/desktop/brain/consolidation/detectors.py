import uuid
from desktop.brain.consolidation.models import Pattern, Habit, LearnedConcept

class PatternDetector:
    def detect_chronological_motifs(self, graph_edges) -> list:
        # Mocking detection of a repeating sequence
        return [Pattern(str(uuid.uuid4()), ["ep1", "ep2"], "WORKFLOW_SEQUENCE", ["n1", "n2"], 3, 0.85)]
    
    def detect_semantic_clusters(self, graph_nodes, graph_edges) -> list:
        # Mocking semantic cluster detection
        return [Pattern(str(uuid.uuid4()), ["n3", "n4"], "SEMANTIC_CLUSTER", ["n3", "n4"], 5, 0.9)]
