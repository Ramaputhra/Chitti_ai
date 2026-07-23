from typing import List, Optional

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import IService


class IRuntimeCapabilityRegistry(IService):
    """
    Tracks all active Capabilities (Filesystem, Process, etc) running in the Operating Runtime.
    """
    def register_capability(self, capability: ICapability) -> None:
        ...

    def get_capability(self, name: str) -> Optional[ICapability]:
        ...

    def get_all_capabilities(self) -> List[ICapability]:
        ...
