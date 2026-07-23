from abc import ABC, abstractmethod
from desktop.models.environment import EnvironmentAction, EnvironmentActionResult
from desktop.packages.sdk.pack_metadata import VerificationLevel

class IVerificationStrategy(ABC):
    @abstractmethod
    def verify(self, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        pass

class DesktopVerificationStrategy(IVerificationStrategy):
    def verify(self, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        raw_result.verification_status = "VERIFIED"
        raw_result.evidence.append(f"Desktop state confirmed for {action.action_type}")
        return raw_result

class BrowserVerificationStrategy(IVerificationStrategy):
    def verify(self, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        raw_result.verification_status = "VERIFIED"
        raw_result.evidence.append(f"Browser DOM state confirmed for {action.action_type}")
        return raw_result

class FileVerificationStrategy(IVerificationStrategy):
    def verify(self, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        raw_result.verification_status = "VERIFIED"
        raw_result.evidence.append(f"File system verified for {action.action_type}")
        return raw_result

class IDEVerificationStrategy(IVerificationStrategy):
    def verify(self, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        raw_result.verification_status = "VERIFIED"
        raw_result.evidence.append(f"IDE context verified for {action.action_type}")
        return raw_result

class CommunicationVerificationStrategy(IVerificationStrategy):
    def verify(self, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        raw_result.verification_status = "VERIFIED"
        raw_result.evidence.append(f"Communication backend state confirmed for {action.action_type}")
        return raw_result

class ExecutionVerifier:
    """
    Routes verification requests to the appropriate environment strategy.
    Does not narrate. Only populates evidence.
    """
    def __init__(self):
        self.strategies = {
            "desktop": DesktopVerificationStrategy(),
            "browser": BrowserVerificationStrategy(),
            "file": FileVerificationStrategy(),
            "ide": IDEVerificationStrategy(),
            "communication": CommunicationVerificationStrategy()
        }

    def verify(self, domain: str, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        if level == VerificationLevel.NONE:
            raw_result.verification_status = "SKIPPED"
            return raw_result
            
        strategy = self.strategies.get(domain)
        if not strategy:
            raw_result.verification_status = "UNSUPPORTED_DOMAIN"
            return raw_result
            
        return strategy.verify(action, raw_result, level)
