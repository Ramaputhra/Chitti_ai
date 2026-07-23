import re
from typing import Dict

class PronunciationManager:
    """
    S36A: Custom Pronunciation Dictionary mapping tech jargon, proper nouns, and user-defined words to phonetic spellings.
    """
    DEFAULT_DICTIONARY: Dict[str, str] = {
        "chatgpt": "Chat G P T",
        "github": "Git Hub",
        "vscode": "V S Code",
        "vs code": "V S Code",
        "rajamouli": "Raja mouli",
        "rama": "Raa ma",
        "sherpa-onnx": "Sherpa O N N X",
        "openai": "Open A I",
        "chitti": "Chit tee"
    }

    def __init__(self):
        self._dictionary = dict(self.DEFAULT_DICTIONARY)

    def add_pronunciation(self, word: str, phonetic: str):
        self._dictionary[word.lower()] = phonetic

    def apply_pronunciation(self, text: str) -> str:
        result = text
        for word, phonetic in self._dictionary.items():
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result = pattern.sub(phonetic, result)
        return result
