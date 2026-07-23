from typing import Optional
from desktop.platform.shared.interfaces.memory_resolver import IMemoryResolver
from desktop.platform.shared.models.entity import PersonEntity, LocationEntity, ResolvedPerson, ResolvedLocation


class MockMemoryResolver(IMemoryResolver):
    """
    A temporary mock implementation of memory resolution using hardcoded dictionaries.
    """
    def __init__(self):
        # Mock database
        self.people_db = {
            "ramu": {"id": "contact_145", "aliases": ["Ramu", "రాము", "Ramu Garu"]},
            "user": {"id": "local_user", "aliases": ["User", "Me", "Admin"]},
        }
        
        self.location_db = {
            "home": {"id": "loc_1", "saved_name": "Home"},
            "office": {"id": "loc_2", "saved_name": "Headquarters"},
        }

    def resolve_person(self, person: PersonEntity) -> Optional[ResolvedPerson]:
        key = person.display_name.lower().strip()
        
        # Simple exact match or alias match
        for db_key, data in self.people_db.items():
            if key == db_key or any(key == alias.lower() for alias in data["aliases"]):
                return ResolvedPerson(
                    original_text=person.original_text,
                    confidence=person.confidence,
                    source=person.source,
                    display_name=person.display_name,
                    contact_id=data["id"],
                    entity_id=data["id"],
                    aliases=data["aliases"],
                    resolution_confidence=1.0
                )
                
        return None

    def resolve_location(self, location: LocationEntity) -> Optional[ResolvedLocation]:
        key = location.display_name.lower().strip()
        
        if key in self.location_db:
            data = self.location_db[key]
            return ResolvedLocation(
                original_text=location.original_text,
                confidence=location.confidence,
                source=location.source,
                display_name=location.display_name,
                coordinates=location.coordinates,
                entity_id=data["id"],
                saved_name=data["saved_name"],
                resolution_confidence=1.0
            )
            
        return None
