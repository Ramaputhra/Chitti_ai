from dataclasses import dataclass
from desktop.models.presentation import PresentationExperienceManifest, PresentationSession

@dataclass
class ExperienceInstance:
    """
    Bridges the static ExperienceManifest and the mutable UI PresentationSession.
    Allows multiple simultaneous instances of the same experience.
    """
    instance_id: str
    manifest: PresentationExperienceManifest
    session: PresentationSession
    is_active: bool = True
