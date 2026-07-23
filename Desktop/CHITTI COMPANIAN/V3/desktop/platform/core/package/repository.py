from abc import ABC, abstractmethod
from typing import List, Optional
from desktop.models.package import PackageManifest

class IPackageRepository(ABC):
    """
    Interface for fetching packages from any source (Local, GitHub, HTTP, Enterprise).
    """
    
    @abstractmethod
    def search(self, query: str) -> List[PackageManifest]:
        """Search the repository for matching packages."""
        pass
        
    @abstractmethod
    def fetch_manifest(self, package_id: str, version: Optional[str] = None) -> Optional[PackageManifest]:
        """Fetch the metadata for a specific package."""
        pass
        
    @abstractmethod
    def download(self, package_id: str, version: Optional[str] = None) -> str:
        """
        Download the physical package and return its local file path.
        """
        pass

class LocalPackageRepository(IPackageRepository):
    """
    Discovers and parses local packages and their capabilities.
    """
    def __init__(self, packages_dir: Optional[str] = None):
        import os
        if not packages_dir:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            self.packages_dir = os.path.join(base, "packages")
        else:
            self.packages_dir = packages_dir

    def search(self, query: str) -> List[PackageManifest]:
        import os
        import json
        from desktop.models.package import PackageComponent, ComponentType
        
        manifests = []
        if not os.path.exists(self.packages_dir):
            return manifests

        for pack_name in os.listdir(self.packages_dir):
            pack_path = os.path.join(self.packages_dir, pack_name)
            manifest_path = os.path.join(pack_path, "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    manifest = PackageManifest(
                        id=data.get("id", pack_name),
                        version=data.get("version", "1.0.0"),
                        type=data.get("type", "PACK"),
                        publisher=data.get("publisher", "Unknown"),
                        description=data.get("description", "")
                    )
                    
                    capabilities_dir = os.path.join(pack_path, "capabilities")
                    if os.path.exists(capabilities_dir):
                        for filename in os.listdir(capabilities_dir):
                            if filename.endswith(".py") and filename != "__init__.py":
                                mod_name = filename[:-3]
                                entrypoint = f"desktop.packages.{pack_name}.capabilities.{mod_name}"
                                comp = PackageComponent(
                                    id=f"{manifest.id}.{mod_name}",
                                    type=ComponentType.CAPABILITY,
                                    entrypoint=entrypoint
                                )
                                manifest.components.append(comp)
                                
                    if not query or query.lower() in manifest.id.lower() or query.lower() in manifest.name.lower():
                        manifests.append(manifest)
                except Exception as e:
                    print(f"[PackageRepository] Failed to load {manifest_path}: {e}")
                    
        return manifests

    def fetch_manifest(self, package_id: str, version: Optional[str] = None) -> Optional[PackageManifest]:
        for manifest in self.search(""):
            if manifest.id == package_id:
                if not version or manifest.version == version:
                    return manifest
        return None

    def download(self, package_id: str, version: Optional[str] = None) -> str:
        # Local packages are already on disk. Return a generic path for lifecycle manager.
        import os
        for pack_name in os.listdir(self.packages_dir):
            pack_path = os.path.join(self.packages_dir, pack_name)
            manifest_path = os.path.join(pack_path, "manifest.json")
            if os.path.exists(manifest_path):
                import json
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("id") == package_id:
                        return pack_path
        return ""
