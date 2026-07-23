from typing import Any, Protocol


class IStorageBackend(Protocol):
    """
    Unified Key-Value interface for a storage backend.
    """
    def initialize(self) -> None: ...
    
    def get(self, key: str) -> Any: ...
    
    def set(self, key: str, value: Any) -> None: ...
    
    def delete(self, key: str) -> None: ...
    
    def clear(self) -> None: ...


class IStorageManager(Protocol):
    """
    Provides access to various persistent and ephemeral storage backends.
    """
    def initialize(self) -> None: ...

    def backend(self, name: str) -> IStorageBackend:
        """Returns a backend by name (e.g., 'keyvalue', 'sqlite', 'cache')."""
        ...
