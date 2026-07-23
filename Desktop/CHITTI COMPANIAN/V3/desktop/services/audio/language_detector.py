class LanguageDetector:
    """
    Stubs the detection of spoken language.
    For now, statically returns 'en' or allows manual override.
    Future: Use a small ONNX model to detect language from audio chunk.
    """
    def __init__(self):
        self._current_default = "en"
        
    def detect(self, audio_data: bytes) -> str:
        # Stub implementation. In the future, this processes the audio_data 
        # to determine if it's English, Hindi, Telugu, etc.
        return self._current_default
        
    def set_default(self, lang_code: str):
        self._current_default = lang_code
