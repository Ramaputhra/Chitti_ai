from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Any, List, Optional
from datetime import datetime
import time

# Generic Types for type-safe contracts
T_Input = TypeVar('T_Input')
T_Output = TypeVar('T_Output')

class TransformationFailure(Exception):
    """Base exception for all deterministic transformation failures."""
    pass

class ValidationFailure(TransformationFailure):
    """Raised when input/output fails structural or semantic validation."""
    pass

class PreconditionsFailure(TransformationFailure):
    """Raised when environment/system constraints prevent transformation."""
    pass

class OutputValidationFailure(TransformationFailure):
    """Raised when the transformation produces structurally invalid output."""
    pass

class InternalRuntimeFailure(TransformationFailure):
    """Raised when the transformation encounters an unexpected internal error."""
    pass

@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class TransformationTelemetry:
    """Standardized observability for every transformation."""
    runtime_name: str
    started_at: datetime
    completed_at: datetime
    duration_ms: float
    success: bool
    failure_reason: Optional[str] = None

@dataclass(frozen=True)
class TransformationResult(Generic[T_Output]):
    output: Optional[T_Output]
    telemetry: TransformationTelemetry

class TransformationContract(ABC, Generic[T_Input, T_Output]):
    """
    The domain contract defining WHAT a runtime transforms.
    Has no knowledge of execution orchestration, telemetry, or side effects.
    """
    
    @property
    @abstractmethod
    def runtime_name(self) -> str:
        """Identifier for telemetry."""
        pass

    @abstractmethod
    def validate_input(self, input_data: T_Input) -> ValidationResult:
        """Validates the immutable input contract before transformation."""
        pass

    @abstractmethod
    def transform(self, input_data: T_Input) -> T_Output:
        """The core deterministic logic mapping Input to Output."""
        pass

    @abstractmethod
    def validate_output(self, output_data: T_Output) -> ValidationResult:
        """Validates the immutable output contract before yielding."""
        pass

class TransformationExecutor:
    """
    Infrastructure layer that enforces HOW every transformation is run:
    timing, validation orchestration, exception normalization, and telemetry generation.
    """
    def execute(self, contract: TransformationContract[T_Input, T_Output], input_data: T_Input) -> TransformationResult[T_Output]:
        start_time = time.time()
        success = False
        failure_reason = None
        output = None
        
        try:
            # 1. Input Validation
            input_validation = contract.validate_input(input_data)
            if not input_validation.valid:
                raise ValidationFailure(f"Input validation failed: {input_validation.errors}")
            
            # 2. Transformation
            output = contract.transform(input_data)
            
            # 3. Output Validation
            output_validation = contract.validate_output(output)
            if not output_validation.valid:
                raise OutputValidationFailure(f"Output validation failed: {output_validation.errors}")
                
            success = True
            
        except TransformationFailure as e:
            failure_reason = str(e)
            raise
        except Exception as e:
            failure_reason = str(e)
            raise InternalRuntimeFailure(f"Unexpected runtime error: {e}")
        finally:
            duration_ms = (time.time() - start_time) * 1000
            telemetry = TransformationTelemetry(
                runtime_name=contract.runtime_name,
                started_at=datetime.fromtimestamp(start_time),
                completed_at=datetime.utcnow(),
                duration_ms=duration_ms,
                success=success,
                failure_reason=failure_reason
            )
            
            # If we succeed, return the result. If we failed, the exception is raised,
            # but in a real system we might dispatch telemetry in the finally block 
            # before the exception propagates. We attach telemetry to the return if successful.
            if success:
                return TransformationResult(output=output, telemetry=telemetry)
