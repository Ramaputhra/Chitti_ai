class LanguageDetector:
    """Lightweight heuristic or classification layer to route audio."""
    def __init__(self):
        pass
        
    def detect_language(self, audio_chunk: bytes) -> str:
        """
        Determines the dominant language in the audio chunk.
        Returns language code (e.g., 'en', 'te').
        """
        # Mock logic: for testing, alternate or return 'en'
        return "en"
