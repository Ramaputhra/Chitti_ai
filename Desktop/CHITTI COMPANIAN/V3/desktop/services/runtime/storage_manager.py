import json
import os
import sqlite3
from typing import Any, Dict

from desktop.platform.configuration.paths import STORAGE_DIR
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.storage import IStorageBackend, IStorageManager


class KeyValueStorage(IStorageBackend):
    def __init__(self, logger: ILoggingService, file_name: str = "kv.json") -> None:
        self.logger = logger
        self.file_path = os.path.join(STORAGE_DIR, file_name)
        self._data: Dict[str, Any] = {}

    def initialize(self) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self._save()

    def clear(self) -> None:
        self._data.clear()
        self._save()


class CacheStorage(IStorageBackend):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._data: Dict[str, Any] = {}

    def initialize(self) -> None:
        pass

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]

    def clear(self) -> None:
        self._data.clear()


class SQLiteStorage(IStorageBackend):
    def __init__(self, logger: ILoggingService, db_name: str = "storage.db") -> None:
        self.logger = logger
        self.db_path = os.path.join(STORAGE_DIR, db_name)

    def initialize(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS kv_store (key TEXT PRIMARY KEY, value TEXT)"
            )

    def get(self, key: str) -> Any:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def set(self, key: str, value: Any) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )

    def delete(self, key: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM kv_store")


class StorageManager(IStorageManager):
    """
    Coordinates access to KeyValue, SQLite, and in-memory Cache backends.
    """
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self.backends: Dict[str, IStorageBackend] = {
            "keyvalue": KeyValueStorage(logger),
            "sqlite": SQLiteStorage(logger),
            "cache": CacheStorage(logger),
        }

    def initialize(self) -> None:
        for backend in self.backends.values():
            backend.initialize()
        self.logger.info("StorageManager initialized all backends")

    def backend(self, name: str) -> IStorageBackend:
        if name not in self.backends:
            raise KeyError(f"Storage backend '{name}' not found")
        return self.backends[name]
