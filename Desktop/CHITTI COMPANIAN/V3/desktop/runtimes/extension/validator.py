from desktop.models.plugin import PluginManifest, TrustLevel
import logging

class PluginValidator:
    """
    Verifies signatures, dependencies, and structure of a PluginManifest.
    Rule 282: Enforces reserved namespaces.
    """
    
    RESERVED_NAMESPACES = {
        "system",
        "knowledge",
        "presentation",
        "behavior",
        "scheduler",
        "execution"
    }

    def validate(self, manifest: PluginManifest) -> bool:
        if not self._verify_signature(manifest):
            return False
            
        if not self._check_reserved_namespaces(manifest):
            return False
            
        if not self._check_duplicate_identifiers(manifest):
            return False
            
        return True

    def _verify_signature(self, manifest: PluginManifest) -> bool:
        # Stub: verify cryptographic signature
        if manifest.trust_level == TrustLevel.UNSAFE:
            logging.warning(f"Plugin {manifest.plugin_id} is running with UNSAFE trust level.")
        return True
        
    def _check_reserved_namespaces(self, manifest: PluginManifest) -> bool:
        # Prevent 3rd party plugins from shadowing built-in platform services
        for provided in manifest.provides:
            namespace = provided.split('.')[0] if '.' in provided else provided
            if namespace in self.RESERVED_NAMESPACES and manifest.trust_level not in [TrustLevel.CORE, TrustLevel.TRUSTED]:
                logging.error(f"Plugin {manifest.plugin_id} attempted to use reserved namespace: {namespace}")
                return False
        return True

    def _check_duplicate_identifiers(self, manifest: PluginManifest) -> bool:
        # Check against the Service Registry for duplicate IDs
        return True


class CompatibilityChecker:
    """
    Rule 283: Checks Platform API version and dependencies before loading.
    """
    def __init__(self, current_platform_version: str):
        self.current_platform_version = current_platform_version

    def check(self, manifest: PluginManifest) -> bool:
        # Ensure the plugin supports this version of CHITTI
        if manifest.minimum_platform_version > self.current_platform_version:
            logging.error(f"Plugin {manifest.plugin_id} requires newer platform: {manifest.minimum_platform_version}")
            return False
            
        if manifest.maximum_platform_version and manifest.maximum_platform_version < self.current_platform_version:
            logging.error(f"Plugin {manifest.plugin_id} is not compatible with this newer platform version.")
            return False
            
        # Stub: check required dependencies against Service Registry
        return True
