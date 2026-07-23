import time
import math
import uuid
from desktop.brain.consolidation.models import LearnedRule, Habit, LearnedConcept, ConsolidatedMemory
from desktop.brain.consolidation.detectors import PatternDetector

class ConsolidationEngine:
    def __init__(self, runtime):
        self.runtime = runtime
        self.detector = PatternDetector()
        self.staging = []
        self.checkpoint = 0
    
    def calculate_memory_strength(self, importance, time_since_reinforcement):
        decay_rate = 0.01
        return importance * math.exp(-decay_rate * time_since_reinforcement)

    def trigger_batch(self, cpu_load, episodes, graph_nodes, graph_edges):
        if cpu_load > 30:
            raise Exception("CPU spike: Consolidation Aborted.")
        
        # Mocks finding a rule explicitly
        rule = LearnedRule("r1", ["ep1"], "Always use dark mode", "Active", 1.0)
        self.staging.append(rule)

        # Mocks extracting habit from sequence pattern
        patterns = self.detector.detect_chronological_motifs(graph_edges)
        for p in patterns:
            habit = Habit(str(uuid.uuid4()), p.source_evidence_ids, "Morning Boot", ["Slack", "Notion"], p.frequency)
            self.staging.append(habit)
        
        # Mocks extracting concept from semantic cluster pattern
        clusters = self.detector.detect_semantic_clusters(graph_nodes, graph_edges)
        for c in clusters:
            concept = LearnedConcept(str(uuid.uuid4()), c.source_evidence_ids, "RAG Architecture", c.involved_node_ids)
            self.staging.append(concept)
        
        # Mocks near-duplicate episode merging
        if len(episodes) >= 2:
            memory = ConsolidatedMemory(str(uuid.uuid4()), episodes, "Researched LangChain", 0.9)
            self.staging.append(memory)
        
        self.runtime.commit(self.staging)
        self.staging.clear()
        self.checkpoint = time.time()
        
    def supersede_rule(self, old_rule_id, new_rule):
        if old_rule_id in self.runtime.artifacts:
            self.runtime.artifacts[old_rule_id].state = "Superseded"
        self.runtime.commit([new_rule])
