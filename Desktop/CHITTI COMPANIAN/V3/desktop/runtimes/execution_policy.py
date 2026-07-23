from enum import Enum
from dataclasses import dataclass
from desktop.models.hardware_profile import CapabilityProfile

class ExecutionTarget(Enum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    OFFLINE_DEGRADED = "OFFLINE_DEGRADED"

class PrivacyLevel(Enum):
    LOW = "LOW"
    HIGH = "HIGH"

class UserPreference(Enum):
    LOCAL_ONLY = "LOCAL_ONLY"
    PREFER_LOCAL = "PREFER_LOCAL"
    BALANCED = "BALANCED"
    PREFER_CLOUD = "PREFER_CLOUD"

@dataclass
class ExecutionPolicyContext:
    service_name: str
    minimum_profile: CapabilityProfile
    privacy_level: PrivacyLevel
    has_internet: bool
    budget_exhausted: bool

class ExecutionPolicyRuntime:
    """
    Evaluates complex rules to determine where a specific AI service should execute.
    This fulfills the ADR for "Local-First, Cloud-Capable AI Routing".
    """
    
    def __init__(self, current_profile: CapabilityProfile, user_preference: UserPreference):
        self.current_profile = current_profile
        self.user_preference = user_preference

    def evaluate_target(self, context: ExecutionPolicyContext) -> ExecutionTarget:
        """
        Determines the execution target (LOCAL, CLOUD, OFFLINE_DEGRADED) for a service.
        """
        # 1. Privacy Override
        if context.privacy_level == PrivacyLevel.HIGH:
            return ExecutionTarget.LOCAL
            
        # 2. Local-Only Preference Override
        if self.user_preference == UserPreference.LOCAL_ONLY:
            return ExecutionTarget.LOCAL
            
        # 3. Budget Exhausted Override
        if context.budget_exhausted:
            return ExecutionTarget.LOCAL

        # 4. Check if Local is capable based on manifest requirements
        # (Simplified logic: assuming CLOUD_REQUIRED means we can't run local)
        is_local_capable = self.current_profile != CapabilityProfile.CLOUD_REQUIRED
        if self.current_profile == CapabilityProfile.LOCAL_LIMITED and context.minimum_profile == CapabilityProfile.LOCAL_FULL:
            is_local_capable = False
            
        # 5. Apply User Preference
        if self.user_preference == UserPreference.PREFER_CLOUD and context.has_internet:
            return ExecutionTarget.CLOUD
            
        if self.user_preference == UserPreference.PREFER_LOCAL:
            if is_local_capable:
                return ExecutionTarget.LOCAL
            elif context.has_internet:
                return ExecutionTarget.CLOUD
            else:
                return ExecutionTarget.OFFLINE_DEGRADED
                
        # 6. Balanced Mode (Default)
        # In balanced mode, we run heavy things in the cloud if capable, otherwise local
        if is_local_capable:
            return ExecutionTarget.LOCAL
        elif context.has_internet:
            return ExecutionTarget.CLOUD
        
        return ExecutionTarget.OFFLINE_DEGRADED
