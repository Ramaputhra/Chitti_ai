import os
import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

@dataclass
class AnimationMetadata:
    id: str
    fps: int
    loop: bool

class AnimationCache:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.animations: Dict[str, List[QPixmap]] = {}
        self.metadata: Dict[str, AnimationMetadata] = {}

    def load_all(self, target_size=(300, 300)):
        if not os.path.exists(self.base_path):
            return
            
        for folder_name in os.listdir(self.base_path):
            folder_path = os.path.join(self.base_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            # Load metadata
            manifest_path = os.path.join(folder_path, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    meta = AnimationMetadata(
                        id=data.get("id", folder_name.lower()),
                        fps=data.get("fps", 24),
                        loop=data.get("loop", True)
                    )
            else:
                meta = AnimationMetadata(id=folder_name.lower(), fps=24, loop=True)
                
            self.metadata[folder_name] = meta
            
            # Load frames
            frames = []
            files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".png")])
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        target_size[0], target_size[1], 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    frames.append(scaled_pixmap)
                    
            if frames:
                self.animations[folder_name] = frames

    def get_frames(self, animation_name: str) -> List[QPixmap]:
        return self.animations.get(animation_name, [])

    def get_metadata(self, animation_name: str) -> Optional[AnimationMetadata]:
        return self.metadata.get(animation_name)
