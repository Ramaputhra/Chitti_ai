from dataclasses import dataclass
import os
import sys

@dataclass(frozen=True)
class AssetManifest:
    asset_identifier: str
    asset_type: str
    version: str
    checksum: str
    destination_path: str
    deployment_required: bool
    integrity_validation_status: str

class InstallationManager:
    def __init__(self, asset_manifest: AssetManifest):
        self.manifest = asset_manifest

    def verify_installation(self) -> bool:
        if getattr(sys, 'frozen', False):
            appdata = os.environ.get("APPDATA", "")
            base_dir = os.path.join(appdata, "CHITTI_V2")
            if not os.path.exists(base_dir):
                print(f"[Verification] Missing directory: {base_dir}")
                return False
                
        if self.manifest.version != "V2":
            return False
            
        print("[Verification] Post-Installation checks passed.")
        return True

    def provision_first_run(self):
        if getattr(sys, 'frozen', False):
            appdata = os.environ.get("APPDATA", "")
            base_dir = os.path.join(appdata, "CHITTI_V2")
            os.makedirs(os.path.join(base_dir, "database"), exist_ok=True)
            os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
