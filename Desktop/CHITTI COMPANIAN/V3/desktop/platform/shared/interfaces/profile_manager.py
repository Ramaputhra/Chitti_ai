from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.profile import BehaviorProfile, IdentityProfile, PreferenceProfile


class IProfileManager(IService):
    """
    Manages the three distinct branches of a user's profile: Identity, Behavior, and Preferences.
    """
    def get_identity(self) -> IdentityProfile:
        ...

    def get_behavior(self) -> BehaviorProfile:
        ...

    def get_preferences(self) -> PreferenceProfile:
        ...

    def update_identity(self, profile: IdentityProfile) -> None:
        ...

    def update_behavior(self, profile: BehaviorProfile) -> None:
        ...

    def update_preferences(self, profile: PreferenceProfile) -> None:
        ...
