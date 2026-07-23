import logging
import os
import subprocess
import time

logger = logging.getLogger(__name__)

class OpenFolderAdapter:
    """
    Physical implementation for the 'sys.folder.open' capability on Windows.
    """
    def execute(self, folder_path: str) -> bool:
        logger.info(f"OpenFolderAdapter: Launching explorer.exe for {folder_path}")
        
        # Verify it's a directory
        if not os.path.exists(folder_path):
            # For "Downloads" we can resolve the canonical path if it's not absolute
            if folder_path.lower() == "downloads":
                folder_path = os.path.expanduser("~/Downloads")
                if not os.path.exists(folder_path):
                    logger.error(f"Path does not exist: {folder_path}")
                    return False
        
        try:
            # Use subprocess to launch explorer asynchronously without blocking
            subprocess.Popen(f'explorer "{os.path.abspath(folder_path)}"')
            logger.info("Explorer launched successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to launch explorer: {e}")
            return False
