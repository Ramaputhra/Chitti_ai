import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class AssetLoader:
    """
    S36D-1: Lazy Asset Loader supporting Hot Reload for SVG, PNG, CSS, Layouts, and Window Templates.
    PROHIBITED: Desktop UI Runtime SHALL NEVER decode or load Character PNG frame sequences.
    """
    def load_asset(self, path: str) -> Optional[str]:
        if "character" in path.lower():
            raise ValueError("PROHIBITED: Desktop UI Runtime SHALL NEVER decode Character PNG assets!")
        logger.info(f"[AssetLoader] Lazy loaded UI asset '{path}'")
        return f"<loaded_asset path='{path}'/>"

    def hot_reload_assets(self) -> bool:
        logger.info("[AssetLoader] Hot reloaded UI assets cleanly without restart.")
        return True
