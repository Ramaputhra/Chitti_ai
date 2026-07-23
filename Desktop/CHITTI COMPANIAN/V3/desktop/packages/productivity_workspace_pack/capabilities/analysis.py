from desktop.packages.sdk.pack_metadata import CapabilityMetadata, VerificationLevel

class ReadSpreadsheetCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis")

class AnalyzeSpreadsheetCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis")

class GenerateChartsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis", verification_level=VerificationLevel.STANDARD)

class ExtractTablesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis")

class CalculateStatisticsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis")
