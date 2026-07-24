"""
Desktop Application Package

This module provides the main application bootstrap and runtime components.
"""
from desktop.app.kernel import BootManager, RuntimeConfiguration

# Backward compatibility aliases - these may not be fully implemented
class ApplicationBootstrap:
    """Stub for backward compatibility - actual implementation may not exist."""
    @staticmethod
    def create_composition_root():
        raise NotImplementedError("ApplicationBootstrap.create_composition_root() is not yet implemented")

class ApplicationRuntime:
    """Stub for backward compatibility - actual implementation may not exist."""
    def __init__(self, container):
        self._container = container
    
    def _initialize_services(self, modes=None):
        raise NotImplementedError("ApplicationRuntime._initialize_services() is not yet implemented")

# Export main classes
__all__ = [
    'BootManager',
    'RuntimeConfiguration', 
    'ApplicationBootstrap',
    'ApplicationRuntime'
]
