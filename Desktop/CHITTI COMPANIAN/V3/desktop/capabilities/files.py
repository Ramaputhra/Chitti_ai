import os
import platform
import logging

logger = logging.getLogger(__name__)

def open_folder(folder_path: str = None) -> None:
    """
    Physical capability to open a folder on the user's desktop.
    Defaults to the Downloads folder if none is provided.
    """
    if not folder_path:
        folder_path = os.path.expanduser("~/Downloads")
        
    logger.info(f"Physically opening folder on desktop: {folder_path}")
    
    # We only run the actual OS command in the real environment, not in headless CI
    if platform.system() == "Windows":
        try:
            os.startfile(folder_path)
            logger.info("Folder opened successfully.")
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
    else:
        logger.info(f"(Simulated open on {platform.system()})")
