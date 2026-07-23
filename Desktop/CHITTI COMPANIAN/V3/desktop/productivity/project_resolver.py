import os
import uuid
import functools
from pathlib import Path
from typing import Optional, List
from desktop.models.identity import ProjectIdentity, Resolver, ProjectDetector

class GitDetector(ProjectDetector):
    def detect(self, canonical_path: str) -> Optional[ProjectIdentity]:
        if (Path(canonical_path) / ".git").is_dir():
            return ProjectIdentity(
                id=f"proj_{uuid.uuid5(uuid.NAMESPACE_URL, canonical_path).hex[:8]}",
                type="PROJECT",
                display_name=Path(canonical_path).name,
                canonical_path=canonical_path,
                project_type="Git",
                repository=Path(canonical_path).name,
                language="Unknown",
                build_system="Unknown",
                metadata={}
            )
        return None

class NodeDetector(ProjectDetector):
    def detect(self, canonical_path: str) -> Optional[ProjectIdentity]:
        if (Path(canonical_path) / "package.json").exists():
            return ProjectIdentity(
                id=f"proj_{uuid.uuid5(uuid.NAMESPACE_URL, canonical_path).hex[:8]}",
                type="PROJECT",
                display_name=Path(canonical_path).name,
                canonical_path=canonical_path,
                project_type="Node.js",
                repository=Path(canonical_path).name,
                language="JavaScript/TypeScript",
                build_system="npm/yarn/pnpm",
                metadata={}
            )
        return None

class PythonDetector(ProjectDetector):
    def detect(self, canonical_path: str) -> Optional[ProjectIdentity]:
        p = Path(canonical_path)
        if (p / "pyproject.toml").exists() or (p / "requirements.txt").exists():
            return ProjectIdentity(
                id=f"proj_{uuid.uuid5(uuid.NAMESPACE_URL, canonical_path).hex[:8]}",
                type="PROJECT",
                display_name=Path(canonical_path).name,
                canonical_path=canonical_path,
                project_type="Python",
                repository=Path(canonical_path).name,
                language="Python",
                build_system="pip/poetry",
                metadata={}
            )
        return None

class RustDetector(ProjectDetector):
    def detect(self, canonical_path: str) -> Optional[ProjectIdentity]:
        if (Path(canonical_path) / "Cargo.toml").exists():
            return ProjectIdentity(
                id=f"proj_{uuid.uuid5(uuid.NAMESPACE_URL, canonical_path).hex[:8]}",
                type="PROJECT",
                display_name=Path(canonical_path).name,
                canonical_path=canonical_path,
                project_type="Rust",
                repository=Path(canonical_path).name,
                language="Rust",
                build_system="cargo",
                metadata={}
            )
        return None

class ProjectResolver(Resolver[str, ProjectIdentity]):
    """
    Identifies logical projects by walking up the directory tree and running
    ProjectDetectors (Rule 49).
    """
    def __init__(self):
        self.detectors: List[ProjectDetector] = [
            NodeDetector(),
            PythonDetector(),
            RustDetector(),
            GitDetector() # Fallback for generic git repos
        ]
        
    @functools.lru_cache(maxsize=128)
    def resolve(self, path: str) -> Optional[ProjectIdentity]:
        if not path:
            return None
            
        try:
            current = Path(path).resolve()
        except Exception:
            return None
            
        # Upward traversal
        while current:
            for detector in self.detectors:
                identity = detector.detect(str(current))
                if identity:
                    return identity
                    
            if current.parent == current:
                # Reached root
                break
            current = current.parent
            
        return None
