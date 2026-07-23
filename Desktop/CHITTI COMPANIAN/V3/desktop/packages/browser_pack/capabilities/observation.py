from desktop.packages.sdk.pack_metadata import CapabilityMetadata
from desktop.models.environment import EnvironmentContext

class ObservePageCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(
            category="Observation",
            supports_background=True,
            supports_cancel=True
        )
    def execute(self, url: str, context: EnvironmentContext):
        pass

class ObserveDownloadCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(
            category="Observation",
            supports_background=True
        )
    def execute(self, download_id: str, context: EnvironmentContext):
        pass

class ObserveLoadingCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(
            category="Observation"
        )
    def execute(self, context: EnvironmentContext):
        pass
