from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class PlanResearchCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Research")
        # Generates ResearchQuestions based on the initial prompt

class SearchAndCollectCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Research")

class EvaluateSourcesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Research")
        # Assigns confidence and credibility to SourceModels

class ExtractKnowledgeCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Research")

class CrossCheckCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Research")
        # Identifies conflicts and updates ResearchHealth

class SynthesizeKnowledgeCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Research")
        # Builds the Knowledge Map

class CompareSourcesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Research")
        # Extracts agreements, contradictions, and citations between multiple sources
