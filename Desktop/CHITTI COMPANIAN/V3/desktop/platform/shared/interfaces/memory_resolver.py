from abc import ABC, abstractmethod
from typing import Optional

from desktop.platform.shared.models.entity import PersonEntity, LocationEntity, ResolvedPerson, ResolvedLocation


class IMemoryResolver(ABC):
    """
    Interface for resolving canonical entities against a semantic memory store.
    """

    @abstractmethod
    def resolve_person(self, person: PersonEntity) -> Optional[ResolvedPerson]:
        """
        Attempts to resolve a PersonEntity to a known identity.
        Returns a ResolvedPerson if successful, or None if no match is found.
        """
        pass

    @abstractmethod
    def resolve_location(self, location: LocationEntity) -> Optional[ResolvedLocation]:
        """
        Attempts to resolve a LocationEntity to a known identity.
        Returns a ResolvedLocation if successful, or None if no match is found.
        """
        pass
