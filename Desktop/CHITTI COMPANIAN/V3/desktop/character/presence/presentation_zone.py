import logging
from desktop.character.presence.desktop_context_manager import DesktopContextManager

logger = logging.getLogger(__name__)

# Backward compatibility alias for PresentationZoneManager
PresentationZoneManager = DesktopContextManager
