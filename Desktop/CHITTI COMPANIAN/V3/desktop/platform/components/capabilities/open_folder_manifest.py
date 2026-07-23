from desktop.models.capability_models import CapabilityManifest, VerificationManifest

def get_open_folder_manifest() -> CapabilityManifest:
    return CapabilityManifest(
        id="sys.folder.open",
        name="Open Folder",
        description="Opens a folder in the native file explorer",
        version="1.0.0",
        category="system.filesystem",
        actions=["OPEN", "LAUNCH", "SHOW"],
        objects=["FOLDER", "DIRECTORY"],
        aliases=["browse to", "open folder", "show folder"],
        required_parameters=["folder_path"],
        optional_parameters=[],
        permissions=["filesystem_read", "process_launch"],
        timeout=5.0,
        retry_policy={"max_retries": 1},
        supports_learning=True,
        verification=VerificationManifest(
            preferred=["window_title"],
            fallback=["process_exists"],
            last_resort=["vision"],
            timeout_seconds=5.0,
            required_confidence=0.95
        )
    )
