import pytest

from desktop.platform.shared.di.container import DIContainer
from desktop.platform.shared.di.exceptions import (
    CircularDependencyError,
    DuplicateRegistrationError,
    MissingDependencyError,
)


class IDatabase: pass
class Database(IDatabase):
    def __init__(self) -> None: pass

class ILogger: pass
class Logger(ILogger):
    def __init__(self) -> None: pass

class IServiceA: pass
class ServiceA(IServiceA):
    def __init__(self, db: IDatabase, logger: ILogger) -> None:
        self.db = db
        self.logger = logger


def test_container_singleton_resolution() -> None:
    container = DIContainer()
    container.register_singleton(IDatabase, Database)
    container.register_singleton(ILogger, Logger)
    container.register_singleton(IServiceA, ServiceA)

    service1 = container.resolve(IServiceA)
    service2 = container.resolve(IServiceA)

    # Validate singleton behavior
    assert service1 is service2
    assert service1.db is service2.db


def test_container_transient_resolution() -> None:
    container = DIContainer()
    container.register_transient(IDatabase, Database)
    
    db1 = container.resolve(IDatabase)
    db2 = container.resolve(IDatabase)
    
    assert db1 is not db2


def test_missing_dependency() -> None:
    container = DIContainer()
    container.register_singleton(IServiceA, ServiceA)
    
    with pytest.raises(MissingDependencyError):
        container.resolve(IServiceA)


def test_duplicate_registration() -> None:
    container = DIContainer()
    container.register_singleton(IDatabase, Database)
    
    with pytest.raises(DuplicateRegistrationError):
        container.register_singleton(IDatabase, Database)


def test_circular_dependency() -> None:
    class ICircularA: pass
    class ICircularB: pass

    class CircularA(ICircularA):
        def __init__(self, b: ICircularB) -> None: pass

    class CircularB(ICircularB):
        def __init__(self, a: ICircularA) -> None: pass

    container = DIContainer()
    container.register_singleton(ICircularA, CircularA)
    container.register_singleton(ICircularB, CircularB)

    with pytest.raises(CircularDependencyError):
        container.resolve(ICircularA)
