from typing import Optional, Dict, Any
from desktop.platform.providers.base import BaseProvider
from desktop.platform.providers.provider_registry import ProviderRegistry
from desktop.platform.providers.provider_health import ProviderHealth

from desktop.platform.providers.ocr.liteocr_provider import LiteOCRProvider
from desktop.platform.providers.ocr.easyocr_provider import EasyOCRProvider

class ProviderManager:
    """
    Central Manager for AI Provider registration, discovery, health checking,
    preferred provider selection, and automatic fallback.
    """
    _instance: Optional['ProviderManager'] = None

    def __init__(self):
        self.registry = ProviderRegistry()
        self._preferred_providers: Dict[str, str] = {
            "ocr": "liteocr",
            "stt": "sherpa_onnx",
            "tts": "piper",
            "vision": "florence2",
            "llm": "ollama"
        }
        self._fallback_providers: Dict[str, str] = {
            "ocr": "easyocr",
            "stt": "faster_whisper",
            "tts": "kokoro",
            "vision": "smolvlm",
            "llm": "lmstudio"
        }
        self._register_default_providers()

    @classmethod
    def get_instance(cls) -> 'ProviderManager':
        if cls._instance is None:
            cls._instance = ProviderManager()
        return cls._instance

    def _register_default_providers(self) -> None:
        """Bootstrap default OCR providers into registry."""
        self.registry.register_provider(LiteOCRProvider())
        self.registry.register_provider(EasyOCRProvider())

    def set_preferred_provider(self, category: str, provider_id: str) -> None:
        self._preferred_providers[category.lower()] = provider_id.lower()

    def get_provider(self, category: str, preferred_id: Optional[str] = None) -> BaseProvider:
        cat = category.lower()
        target_id = (preferred_id or self._preferred_providers.get(cat, "auto")).lower()

        # Handle AUTO mode or specific preferred provider ID
        if target_id == "auto":
            target_id = self._preferred_providers.get(cat, "liteocr")

        primary_provider = self.registry.get_provider(cat, target_id)

        # Health & Availability Check
        if primary_provider and ProviderHealth.is_available(primary_provider):
            print(f"[ProviderManager] Selected preferred provider '{primary_provider.provider_id}' for category '{cat}'")
            return primary_provider

        # Fallback Trigger
        fallback_id = self._fallback_providers.get(cat, "easyocr")
        print(f"[ProviderManager] Primary provider '{target_id}' unavailable/unhealthy. Triggering Automatic Fallback to '{fallback_id}'")
        fallback_provider = self.registry.get_provider(cat, fallback_id)

        if fallback_provider:
            return fallback_provider

        raise RuntimeError(f"No healthy provider available for category '{category}'")
