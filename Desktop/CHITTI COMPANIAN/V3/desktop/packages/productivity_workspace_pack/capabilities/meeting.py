from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ResolveMeetingCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Meeting")

class GatherMeetingContextCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Meeting")
        # Aggregates previous meetings, timeline, git branches, tasks, chats.

class GenerateMeetingInsightsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Meeting")
        # Proactive observations ("John hasn't replied", "Proposal changed").

class PrepareMeetingWorkspaceCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Meeting")
        # Orchestrates Desktop Pack to open Teams, Agenda, Proposal, arranges windows.

class ProcessMeetingFollowUpCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Meeting")
        # Structured outputs: extracts decisions, action items, drafts email.
