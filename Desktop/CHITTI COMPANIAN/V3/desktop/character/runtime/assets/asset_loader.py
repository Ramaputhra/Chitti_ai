import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class LoadedBehaviorClip:
    behavior_id: str
    behavior_name: str
    category: str
    clip_dir: str
    metadata: Dict[str, Any]
    frame_paths: List[str]
    sound_path: Optional[str]
    mtime: float = 0.0

class AssetLoader:
    """
    S36A / S36B: Lazy Asset Loader loading 2D PNG frame sequences, behavior.json, and sound.wav
    from canonical Character Studio (`desktop/character/studio/assets/runtime/behaviors/`).
    Supports hot reloading when PNG sequences or behavior.json files change.
    """
    def __init__(self, studio_behaviors_root: Optional[str] = None):
        if studio_behaviors_root:
            self.root = studio_behaviors_root
        else:
            v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            self.root = os.path.join(v3_root, "desktop", "character", "studio", "assets", "runtime", "behaviors")
        self._clip_cache: Dict[str, LoadedBehaviorClip] = {}

    def find_behavior_dir(self, behavior_id_or_name: str) -> Optional[str]:
        target = behavior_id_or_name.lower()
        if not os.path.exists(self.root):
            return None

        for cat in os.listdir(self.root):
            cat_dir = os.path.join(self.root, cat)
            if not os.path.isdir(cat_dir):
                continue
            for b_folder in os.listdir(cat_dir):
                b_path = os.path.join(cat_dir, b_folder)
                if not os.path.isdir(b_path):
                    continue
                
                json_path = os.path.join(b_path, "behavior.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data.get("behavior_id", "").lower() == target or data.get("behavior_name", "").lower() == target or b_folder.lower() == target:
                            return b_path
                    except Exception:
                        pass
        return None

    def load_clip(self, behavior_id_or_name: str, force_reload: bool = False) -> Optional[LoadedBehaviorClip]:
        b_dir = self.find_behavior_dir(behavior_id_or_name)
        if not b_dir:
            logger.warning(f"[AssetLoader] Behavior '{behavior_id_or_name}' not found in {self.root}")
            return None

        json_path = os.path.join(b_dir, "behavior.json")
        current_mtime = os.path.getmtime(json_path) if os.path.exists(json_path) else 0.0

        if not force_reload and b_dir in self._clip_cache:
            cached = self._clip_cache[b_dir]
            if cached.mtime == current_mtime:
                return cached

        # Load metadata
        metadata = {}
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        # Load frame paths
        frames = []
        for i in range(1, 15):
            fn = f"Frame{i:02d}.png"
            fp = os.path.join(b_dir, fn)
            if os.path.exists(fp):
                frames.append(fp)

        # Load sound path
        sound_file = metadata.get("sound_file", "sound.wav")
        sound_path = os.path.join(b_dir, sound_file) if os.path.exists(os.path.join(b_dir, sound_file)) else None

        clip = LoadedBehaviorClip(
            behavior_id=metadata.get("behavior_id", behavior_id_or_name),
            behavior_name=metadata.get("behavior_name", behavior_id_or_name),
            category=metadata.get("category", "system"),
            clip_dir=b_dir,
            metadata=metadata,
            frame_paths=frames,
            sound_path=sound_path,
            mtime=current_mtime
        )

        self._clip_cache[b_dir] = clip
        logger.info(f"[AssetLoader] Loaded clip '{clip.behavior_id}' ({len(frames)} frames). Hot reload ready.")
        return clip

    def check_hot_reload(self, behavior_id_or_name: str) -> bool:
        clip = self.load_clip(behavior_id_or_name, force_reload=True)
        return clip is not None
