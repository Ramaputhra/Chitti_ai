from desktop.models.package import PackageManifest, PackageLifecycle
import logging

class LifecycleManager:
    """
    Rule 308: Installation and activation are separate operations.
    Handles physical installation, extraction, and validation of the downloaded package.
    """
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    def verify_package(self, manifest: PackageManifest, file_path: str) -> bool:
        """
        Verifies checksum and signature of the downloaded package.
        """
        self._emit("PackageLifecycleChanged", {"package_id": manifest.id, "state": PackageLifecycle.VERIFIED.value})
        # Stub: perform SHA256 and signature checks
        return True

    def install_package(self, manifest: PackageManifest, file_path: str) -> bool:
        """
        Extracts the package to the secure platform directories.
        Does NOT register or activate components.
        """
        if not self.verify_package(manifest, file_path):
            logging.error(f"Failed to verify package {manifest.id}")
            return False
            
        # Stub: Extract zip/tar to ~/.gemini/chitti/packages/<id>/<version>
        self._emit("PackageLifecycleChanged", {"package_id": manifest.id, "state": PackageLifecycle.INSTALLED.value})
        return True
        
    def uninstall_package(self, package_id: str) -> bool:
        """
        Rule 311: Every package must be removable without damaging the platform.
        Removes physical files.
        """
        self._emit("PackageLifecycleChanged", {"package_id": package_id, "state": PackageLifecycle.REMOVED.value})
        return True
