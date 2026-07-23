from desktop.packages.sdk.pack_metadata import CapabilityMetadata, VerificationLevel

class PrepareEnvironmentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Activity", verification_level=VerificationLevel.STRICT)

class InteractiveRecoveryCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Activity", requires_user_confirmation=True)

class VerifyResumeStateCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Activity", verification_level=VerificationLevel.STRICT)

class CaptureActivityCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Activity", supports_background=True)

class GenerateResumeSummaryCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Activity")

class AnalyzeActivityCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Activity")
