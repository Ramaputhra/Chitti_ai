from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ReadProblemsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Diagnostics")

class ReadLogsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Diagnostics")

class StartDebuggerCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Diagnostics")

class StopDebuggerCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Diagnostics")
