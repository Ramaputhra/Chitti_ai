from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ViewScheduleCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Calendar")

class CreateEventCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Calendar", requires_user_confirmation=True)

class UpdateEventCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Calendar", requires_user_confirmation=True)

class CancelEventCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Calendar", requires_user_confirmation=True)

class FindAvailabilityCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Calendar")

class ReminderCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Calendar")

class WatchCalendarChangesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)
