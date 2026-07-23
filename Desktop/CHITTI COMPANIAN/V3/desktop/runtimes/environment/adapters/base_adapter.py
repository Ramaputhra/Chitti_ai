from abc import ABC, abstractmethod
from desktop.models.environment import EnvironmentAction, EnvironmentContext, AdapterHealth

class IEnvironmentAdapter(ABC):
    """
    Strict Interface Contract for all Environment Adapters (Browser, Desktop, IDE, etc.).
    Rule 353: Adapters must remain stateless translators.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def check_health(self) -> AdapterHealth:
        pass

    @abstractmethod
    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> bool:
        """
        Translate generic action into native script execution.
        """
        pass

    @abstractmethod
    def dispose(self) -> None:
        pass
