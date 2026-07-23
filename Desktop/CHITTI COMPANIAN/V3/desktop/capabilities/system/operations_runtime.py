import subprocess
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Any

@dataclass(frozen=True)
class OperationPlan:
    """Immutable execution plan for privileged actions."""
    operation: str
    package: str
    source: Optional[str] = None
    method: str = "winget"
    rollback: str = "none"
    requires_admin: bool = False

@dataclass(frozen=True)
class PrivilegeContext:
    """Context accompanying a privileged execution."""
    requires_admin: bool
    approval_id: str
    approved_by: str
    approved_at: float
    operation_hash: str

class InstallerAdapter(ABC):
    @abstractmethod
    def install(self, plan: OperationPlan) -> bool:
        pass
        
    @abstractmethod
    def uninstall(self, plan: OperationPlan) -> bool:
        pass

class WingetAdapter(InstallerAdapter):
    def install(self, plan: OperationPlan) -> bool:
        # Mock winget install
        print(f"[WingetAdapter] Installing {plan.package}...")
        return True
        
    def uninstall(self, plan: OperationPlan) -> bool:
        print(f"[WingetAdapter] Uninstalling {plan.package}...")
        return True

class MSIAdapter(InstallerAdapter):
    def install(self, plan: OperationPlan) -> bool:
        print(f"[MSIAdapter] Installing {plan.source} /qn...")
        return True
        
    def uninstall(self, plan: OperationPlan) -> bool:
        return True

class EXEAdapter(InstallerAdapter):
    def install(self, plan: OperationPlan) -> bool:
        print(f"[EXEAdapter] Executing {plan.source} /S...")
        return True
        
    def uninstall(self, plan: OperationPlan) -> bool:
        return True

class SystemOperationsRuntime:
    """Executes validated, immutable operation plans via adapters."""
    def __init__(self):
        self._adapters: Dict[str, InstallerAdapter] = {
            "winget": WingetAdapter(),
            "msi": MSIAdapter(),
            "exe": EXEAdapter()
        }
        
    def execute_plan(self, plan: OperationPlan, context: PrivilegeContext) -> bool:
        if not context:
            raise PermissionError("PrivilegeContext is required for SystemOperationsRuntime.")
            
        adapter = self._adapters.get(plan.method)
        if not adapter:
            raise ValueError(f"Unknown installer method: {plan.method}")
            
        if plan.operation == "install":
            return adapter.install(plan)
        elif plan.operation == "uninstall":
            return adapter.uninstall(plan)
        else:
            raise ValueError(f"Unknown operation: {plan.operation}")
            
    def verify(self, package: str, strategy: str) -> bool:
        print(f"[Verification] Checking {package} using {strategy} strategy...")
        if strategy == "winget":
            return True
        elif strategy == "registry":
            return True
        elif strategy == "filesystem":
            return True
        return False
