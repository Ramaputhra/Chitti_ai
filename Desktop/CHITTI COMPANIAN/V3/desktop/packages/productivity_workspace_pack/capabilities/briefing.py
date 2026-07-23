from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class PrioritizeBriefingItemsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Briefing")
        # Sorts and tags items as Urgent, Important, Review, Information

class GenerateBriefingInsightsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Briefing")
        # Generates actionable observations ("Meeting starts in 25 min")

class GenerateCompanionSuggestionsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Briefing")
        # Generates quick action suggestions ("Resume React Project")

class RetrieveBriefingMemoryCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Briefing")
        # Filters out already briefed items
