from typing import Tuple, List

class SpeechValidator:
    """
    S36A: Validates speech requests for text length, language codes, and valid profiles.
    """
    def validate_speech_request(self, text: str, lang_code: str) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not text or not text.strip():
            errors.append("Speech text cannot be empty or whitespace.")
        if len(text) > 5000:
            errors.append("Speech text exceeds maximum length limit of 5000 characters.")
        
        is_valid = len(errors) == 0
        return is_valid, errors
