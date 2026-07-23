class DIException(Exception):
    """Base exception for Dependency Injection errors."""
    pass

class DuplicateRegistrationError(DIException):
    """Raised when a service interface is registered more than once."""
    pass

class MissingDependencyError(DIException):
    """Raised when a required dependency has not been registered."""
    pass

class CircularDependencyError(DIException):
    """Raised when a circular dependency chain is detected during resolution."""
    pass
