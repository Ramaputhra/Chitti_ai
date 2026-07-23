from typing import List, Dict, Set
from desktop.models.package import PackageManifest, PackageBundle
from desktop.platform.core.package.repository import IPackageRepository

class DependencyResolver:
    """
    Rule 310: Package dependencies are declarative.
    Resolves the full transitive closure of dependencies for a given bundle or manifest.
    """
    def __init__(self, repository: IPackageRepository):
        self.repository = repository

    def resolve_bundle(self, bundle: PackageBundle) -> List[PackageManifest]:
        """
        Takes a bundle and returns the ordered list of all required PackageManifests, 
        including transitive dependencies.
        """
        all_required = list(bundle.required_packages)
        return self.resolve_manifests(all_required)

    def resolve_manifests(self, root_package_ids: List[str]) -> List[PackageManifest]:
        """
        Given a list of package IDs, returns the topologically sorted list of PackageManifests
        that must be installed (least dependent first).
        """
        resolved_manifests: Dict[str, PackageManifest] = {}
        visited: Set[str] = set()
        
        for pkg_id in root_package_ids:
            self._resolve_recursive(pkg_id, visited, resolved_manifests)
            
        # Stub: A real implementation would perform a topological sort here based on dependencies.
        # For now, we return them in discovery order.
        return list(resolved_manifests.values())
        
    def _resolve_recursive(self, package_id: str, visited: Set[str], resolved_manifests: Dict[str, PackageManifest]):
        if package_id in visited:
            return
            
        visited.add(package_id)
        
        manifest = self.repository.fetch_manifest(package_id)
        if not manifest:
            raise ValueError(f"Could not resolve dependency: {package_id}")
            
        resolved_manifests[package_id] = manifest
        
        for dep_id in manifest.dependencies:
            self._resolve_recursive(dep_id, visited, resolved_manifests)
