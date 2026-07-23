"""
Input/Output Validation Module

Provides request/response validation for production-ready capabilities.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from pydantic import BaseModel, Field, field_validator, ValidationError
from enum import Enum
import re


class ErrorCode(str, Enum):
    """Standardized error codes for CHITTI."""
    # Validation errors (1000-1999)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FIELD_FORMAT = "INVALID_FIELD_FORMAT"
    VALUE_OUT_OF_RANGE = "VALUE_OUT_OF_RANGE"
    
    # Execution errors (2000-2999)
    EXECUTION_ERROR = "EXECUTION_ERROR"
    CAPABILITY_NOT_FOUND = "CAPABILITY_NOT_FOUND"
    CAPABILITY_UNAVAILABLE = "CAPABILITY_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    
    # System errors (3000-3999)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    
    # Permission errors (4000-4999)
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = False
    error: str
    error_code: ErrorCode
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standard success response format."""
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ExecutionRequest(BaseModel):
    """Validated execution request."""
    capability: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=100)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    
    @field_validator('capability', 'action')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError("Must be a valid identifier (letters, numbers, underscore, hyphen)")
        return v
    
    @field_validator('parameters')
    @classmethod
    def validate_parameters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        # Limit parameter size to prevent abuse
        import json
        size = len(json.dumps(v))
        if size > 100_000:  # 100KB
            raise ValueError("Parameters too large (max 100KB)")
        return v


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., pattern="^(healthy|unhealthy|degraded)$")
    version: str
    uptime_seconds: float
    components: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


def validate_input(schema: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
    """
    Validate input data against a Pydantic schema.
    Raises ValidationError with structured error messages.
    """
    return schema.model_validate(data)


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input to prevent injection attacks."""
    if not isinstance(value, str):
        return str(value)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Trim to max length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()


def sanitize_dict(data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
    """Recursively sanitize dictionary values."""
    if max_depth <= 0:
        return {}
    
    result = {}
    for key, value in data.items():
        # Sanitize key
        safe_key = sanitize_string(str(key), max_length=100)
        
        if isinstance(value, str):
            result[safe_key] = sanitize_string(value)
        elif isinstance(value, dict):
            result[safe_key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            result[safe_key] = [
                sanitize_string(v) if isinstance(v, str) else v
                for v in value[:100]  # Limit list size
            ]
        else:
            result[safe_key] = value
    
    return result


class RequestValidator:
    """
    Validates incoming requests with additional security checks.
    """
    
    @staticmethod
    def validate_execution_request(data: Dict[str, Any]) -> ExecutionRequest:
        """
        Validate and sanitize an execution request.
        """
        # Sanitize input first
        sanitized = sanitize_dict(data)
        
        # Validate with schema
        try:
            return ExecutionRequest.model_validate(sanitized)
        except ValidationError as e:
            # Convert to user-friendly error
            errors = e.errors()
            first_error = errors[0] if errors else {}
            raise ValueError(
                f"{ErrorCode.INVALID_INPUT}: {first_error.get('msg', 'Invalid input')}"
            )
    
    @staticmethod
    def validate_json_size(data: str, max_size: int = 10_000_000) -> bool:
        """Check if JSON data is within size limits."""
        return len(data.encode('utf-8')) <= max_size


class ResponseBuilder:
    """
    Builds standardized responses.
    """
    
    @staticmethod
    def success(data: Any = None, message: str = None) -> Dict[str, Any]:
        """Build a success response."""
        response = {"success": True}
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return response
    
    @staticmethod
    def error(
        error_code: ErrorCode,
        message: str,
        details: Dict[str, Any] = None,
        request_id: str = None
    ) -> Dict[str, Any]:
        """Build an error response."""
        response = {
            "success": False,
            "error": message,
            "error_code": error_code.value
        }
        if details:
            response["details"] = details
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def from_exception(exc: Exception, request_id: str = None) -> Dict[str, Any]:
        """Build an error response from an exception."""
        error_code = ErrorCode.INTERNAL_ERROR
        message = "An internal error occurred"
        
        if isinstance(exc, ValueError):
            error_code = ErrorCode.INVALID_INPUT
            message = str(exc)
        elif isinstance(exc, TimeoutError):
            error_code = ErrorCode.TIMEOUT
            message = "Operation timed out"
        elif isinstance(exc, ValidationError):
            error_code = ErrorCode.VALIDATION_ERROR
            message = "Validation failed"
        
        return ResponseBuilder.error(error_code, message, request_id=request_id)
