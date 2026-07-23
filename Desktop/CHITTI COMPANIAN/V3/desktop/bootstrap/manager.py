from dataclasses import dataclass
from typing import List
from desktop.bootstrap.config import ConfigurationLoader
from desktop.bootstrap.container import DependencyContainer, ServiceRegistry, ServiceDeclaration
from desktop.bootstrap.lifecycle import LifecycleManager, LifecycleState

@dataclass
class BootstrapManifest:
    required_services: List[str]
    optional_services: List[str]
    failure_policy: str

class BootstrapManager:
    def __init__(self, manifest: BootstrapManifest):
        self.manifest = manifest
        self.registry = ServiceRegistry()
        self.lifecycle = LifecycleManager(self.registry)
        self.config_loader = ConfigurationLoader()
        self.container = DependencyContainer(self.registry)

    def boot(self):
        try:
            self.lifecycle.transition(LifecycleState.PRE_INIT)
            self.config_loader.load()
            
            self.lifecycle.transition(LifecycleState.STARTING)
            
            decls = [
                ServiceDeclaration(identifier=s, dependencies=[], initialization_order=i, shutdown_order=i)
                for i, s in enumerate(self.manifest.required_services)
            ]
            
            self.container.wire(decls)
            self.config_loader.freeze()
            
            self.lifecycle.transition(LifecycleState.RUNNING)
            print("[BootstrapManager] Successfully entered RUNNING state.")
            
        except Exception as e:
            self.lifecycle.handle_crash(e)

    def shutdown(self):
        self.lifecycle.transition(LifecycleState.SHUTTING_DOWN)
        self.lifecycle.shutdown_manager.shutdown()
        self.lifecycle.transition(LifecycleState.TERMINATED)
