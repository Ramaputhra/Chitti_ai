from dataclasses import dataclass, field
import json
import os

@dataclass
class PlatformSettings:
    """
    HOW CHITTI behaves (Settings), distinct from WHO the user is (Profile).
    """
    theme: str = "dark"
    accent_color: str = "blue"
    animation_fps: int = 60
    auto_update: bool = True
    wake_word_enabled: bool = True
    privacy_mode: str = "standard" # strict, standard, relaxed
    logging_level: str = "INFO"
    developer_mode: bool = False
    experimental_features: bool = False

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "accent_color": self.accent_color,
            "animation_fps": self.animation_fps,
            "auto_update": self.auto_update,
            "wake_word_enabled": self.wake_word_enabled,
            "privacy_mode": self.privacy_mode,
            "logging_level": self.logging_level,
            "developer_mode": self.developer_mode,
            "experimental_features": self.experimental_features
        }

    @staticmethod
    def from_dict(data: dict) -> 'PlatformSettings':
        return PlatformSettings(
            theme=data.get("theme", "dark"),
            accent_color=data.get("accent_color", "blue"),
            animation_fps=data.get("animation_fps", 60),
            auto_update=data.get("auto_update", True),
            wake_word_enabled=data.get("wake_word_enabled", True),
            privacy_mode=data.get("privacy_mode", "standard"),
            logging_level=data.get("logging_level", "INFO"),
            developer_mode=data.get("developer_mode", False),
            experimental_features=data.get("experimental_features", False)
        )
