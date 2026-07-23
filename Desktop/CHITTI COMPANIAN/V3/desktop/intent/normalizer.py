import json
from pathlib import Path

class TextNormalizer:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.dictionary = {}
        
    def load(self):
        norm_path = self.config_dir / "normalization" / "normalization.json"
        if norm_path.exists():
            with open(norm_path, 'r', encoding='utf-8') as f:
                self.dictionary = json.load(f)
                
    def normalize(self, text: str) -> str:
        """Converts multilingual/colloquial text to canonical tokens."""
        text = text.lower()
        words = text.split()
        normalized_words = []
        
        for word in words:
            found = False
            for canonical, synonyms in self.dictionary.items():
                if word in synonyms:
                    normalized_words.append(canonical)
                    found = True
                    break
            if not found:
                normalized_words.append(word)
                
        return " ".join(normalized_words)
