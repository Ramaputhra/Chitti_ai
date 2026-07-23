import unittest
from desktop.updater.manager import UpdateManifest
from desktop.updater.installer_hooks import AssetManifest

class TestEE8Deployment(unittest.TestCase):
    def test_update_manifest_immutability(self):
        manifest = UpdateManifest(
            package_identifier="pkg_1",
            version="V2",
            build_identifier="build_1",
            release_timestamp="now",
            package_checksum="hash",
            minimum_compatible_build="build_0",
            package_size=100,
            digital_signature_status="VALID",
            release_channel="Stable",
            mandatory_update=True
        )
        with self.assertRaises(Exception):
            manifest.version = "V3"
            
    def test_asset_manifest_immutability(self):
        manifest = AssetManifest(
            asset_identifier="ast_1",
            asset_type="theme",
            version="V2",
            checksum="hash",
            destination_path="/",
            deployment_required=True,
            integrity_validation_status="VALID"
        )
        with self.assertRaises(Exception):
            manifest.version = "V3"
            
if __name__ == '__main__':
    unittest.main()
