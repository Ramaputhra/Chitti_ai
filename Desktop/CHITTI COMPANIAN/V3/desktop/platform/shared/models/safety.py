from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


@dataclass(frozen=True)
class PromptValidationResult:
    status: ValidationStatus
    reason: str = ""


@dataclass(frozen=True)
class ResponseValidationResult:
    status: ValidationStatus
    reason: str = ""


@dataclass(frozen=True)
class ToolValidationResult:
    status: ValidationStatus
    reason: str = ""
