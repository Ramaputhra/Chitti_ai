import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class IdentityProfile:
    character_id: str
    display_name: str
    short_name: str
    creator: str
    platform_version: str
    identity_version: str
    profile_version: str
    mission: str
    personality_profile: str
    default_language: str
    default_voice: str
    creation_date: str
    documents: Dict[str, str] = field(default_factory=dict)
    mtime: float = 0.0

class IdentityLoader:
    """
    S36C-R1: Loads IdentityProfile and associated Markdown identity documents.
    Supports hot reload checking.
    """
    def __init__(self, profiles_root: Optional[str] = None):
        if profiles_root:
            self.root = profiles_root
        else:
            self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "profiles"))

    def load_profile(self, profile_name: str = "default", force_reload: bool = False) -> Optional[IdentityProfile]:
        p_dir = os.path.join(self.root, profile_name)
        json_path = os.path.join(p_dir, "identity.json")

        if not os.path.exists(json_path):
            logger.error(f"[IdentityLoader] Profile directory or identity.json not found at '{p_dir}'")
            return None

        current_mtime = os.path.getmtime(json_path)
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load all markdown documents
        docs = {}
        for fn in os.listdir(p_dir):
            if fn.endswith(".md"):
                key = fn[:-3]
                fp = os.path.join(p_dir, fn)
                with open(fp, "r", encoding="utf-8") as f:
                    docs[key] = f.read()

        profile = IdentityProfile(
            character_id=data.get("character_id", "CHR_ID_DEFAULT"),
            display_name=data.get("display_name", "CHITTI"),
            short_name=data.get("short_name", "CHITTI"),
            creator=data.get("creator", "Rama"),
            platform_version=data.get("platform_version", "2.0.0"),
            identity_version=data.get("identity_version", "1.0.0"),
            profile_version=data.get("profile_version", "1.0.0"),
            mission=data.get("mission", "Desktop Companion"),
            personality_profile=data.get("personality_profile", "friendly"),
            default_language=data.get("default_language", "en"),
            default_voice=data.get("default_voice", "en-US-Neural"),
            creation_date=data.get("creation_date", "2026-07-22"),
            documents=docs,
            mtime=current_mtime
        )
        logger.info(f"[IdentityLoader] Profile '{profile.display_name}' loaded successfully with {len(docs)} documents.")
        return profile
