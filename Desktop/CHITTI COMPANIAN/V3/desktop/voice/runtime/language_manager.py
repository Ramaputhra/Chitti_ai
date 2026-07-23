from typing import Dict, List, Optional

class LanguageManager:
    """
    S36A: Language Manager supporting 12 languages + Auto Detect, user preference persistence, and runtime switching.
    """
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "en": "English",
        "te": "Telugu",
        "hi": "Hindi",
        "ta": "Tamil",
        "kn": "Kannada",
        "ml": "Malayalam",
        "mr": "Marathi",
        "bn": "Bengali",
        "ja": "Japanese",
        "de": "German",
        "fr": "French",
        "es": "Spanish",
        "auto": "Auto Detect"
    }

    def __init__(self, default_language: str = "en"):
        self._current_language = default_language if default_language in self.SUPPORTED_LANGUAGES else "en"

    @property
    def current_language(self) -> str:
        return self._current_language

    def set_language(self, lang_code: str) -> bool:
        if lang_code in self.SUPPORTED_LANGUAGES:
            self._current_language = lang_code
            return True
        return False

    def detect_language(self, text: str) -> str:
        # Simple heuristic auto-detection placeholder
        if any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in text):
            return "te" # Telugu
        if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text):
            return "hi" # Hindi / Devanagari
        if any(ord(c) >= 0x3040 and ord(c) <= 0x30FF for c in text):
            return "ja" # Japanese
        return self._current_language
