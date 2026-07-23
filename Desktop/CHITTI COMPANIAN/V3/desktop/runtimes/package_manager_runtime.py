import logging
from typing import Dict, Any
from desktop.models.package import PackageBundle, PackageManifest, PackageLifecycle, ComponentType
from desktop.platform.core.package.repository import IPackageRepository
from desktop.runtimes.package.dependency_resolver import DependencyResolver
from desktop.runtimes.package.lifecycle_manager import LifecycleManager

from desktop.models.lifecycle import IRuntime, HealthState

class PackageManagerRuntime(IRuntime):
    """
    Rule 313: Components register through their owning runtime. Package Manager only routes.
    Orchestrates the resolution, installation, and registration routing of packages.
    """
    def __init__(self, repository: IPackageRepository, event_bus=None, target_runtimes=None):
        self.repository = repository
        self.event_bus = event_bus
        self.resolver = DependencyResolver(repository)
        self.lifecycle_manager = LifecycleManager(event_bus)
        
        # Dependency Injection of target runtimes (ServiceRegistry, PresentationRuntime, etc.)
        self.target_runtimes = target_runtimes or {}

    @property
    def dependencies(self):
        return []

    async def initialize(self, context) -> bool:
        if not self.event_bus and hasattr(context, 'event_bus'):
            self.event_bus = context.event_bus
        return True

    async def start(self) -> bool:
        logging.info("[PackageManagerRuntime] Started.")
        return True

    async def stop(self) -> bool:
        logging.info("[PackageManagerRuntime] Stopped.")
        return True

    async def shutdown(self) -> bool:
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    def install_bundle(self, bundle: PackageBundle):
        """
        Installs a full bundle and all its transitive dependencies.
        """
        self._emit("BundleInstallationStarted", {"bundle_id": bundle.bundle_id})
        
        # 1. Resolve Dependencies
        manifests = self.resolver.resolve_bundle(bundle)
        
        # 2. Process each package in order
        for manifest in manifests:
            self.install_package(manifest)
            
        self._emit("BundleInstallationCompleted", {"bundle_id": bundle.bundle_id})

    def install_package(self, manifest: PackageManifest):
        """
        Downloads, installs, and routes the components of a single package.
        """
        self._emit("PackageLifecycleChanged", {"package_id": manifest.id, "state": PackageLifecycle.DOWNLOADED.value})
        
        # Download (Stubbed path)
        file_path = self.repository.download(manifest.id, manifest.version)
        
        # Install (Extraction & Verification)
        if not self.lifecycle_manager.install_package(manifest, file_path):
            raise RuntimeError(f"Failed to install package {manifest.id}")
            
        # Register Components (Rule 313 routing)
        self._route_components(manifest)
        
        self._emit("PackageLifecycleChanged", {"package_id": manifest.id, "state": PackageLifecycle.REGISTERED.value})
        
    def _route_components(self, manifest: PackageManifest):
        """
        Rule 313: Distributes components inside the package to their respective owning runtimes.
        """
        for component in manifest.components:
            runtime = self.target_runtimes.get(component.type)
            if runtime:
                try:
                    # Generic registration interface expected on target runtimes
                    runtime.register_component(manifest.id, component)
                except Exception as e:
                    logging.error(f"Runtime {component.type} failed to register component {component.id}: {e}")
            else:
                logging.warning(f"No runtime configured to handle component type {component.type.value}")
