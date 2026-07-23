"""
Filesystem Shared Primitive

This module is part of the frozen filesystem infrastructure.
Only functionality proven by at least two capabilities may be added.
Capability-specific logic is prohibited.
"""
import os
import pathlib

def expand_environment_variables(path: str) -> str:
    """Expands environment variables and user home (e.g. ~)."""
    return os.path.expanduser(os.path.expandvars(path))

def resolve_absolute_path(path: str) -> str:
    """Resolves an absolute path from a potentially relative one."""
    return os.path.abspath(path)

def normalize_path(path: str) -> str:
    """Combines expansion and resolution into a fully normalized path."""
    return resolve_absolute_path(expand_environment_variables(path))

def is_same_path(path1: str, path2: str) -> bool:
    """Checks if two paths point to the exact same file/directory."""
    try:
        return os.path.samefile(normalize_path(path1), normalize_path(path2))
    except (FileNotFoundError, OSError):
        # If either doesn't exist, we fall back to absolute path comparison
        return normalize_path(path1).lower() == normalize_path(path2).lower()
