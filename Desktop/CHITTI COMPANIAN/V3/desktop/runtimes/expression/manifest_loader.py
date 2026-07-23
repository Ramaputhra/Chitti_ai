import json
import os
from typing import Dict, Any

class ExpressionManifestLoader:
    """
    Loads declarative expression definitions from expressions.json.
    (Rule 38: Declarative Expression Assets)
    """
    def __init__(self, manifest_path: str = None):
        if manifest_path is None:
            manifest_path = os.path.join(os.path.dirname(__file__), "expressions.json")
        self.manifest_path = manifest_path
        self.expressions: Dict[str, Any] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.manifest_path):
            # Fallback empty config
            self.expressions = {}
            return
            
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            self.expressions = json.load(f)

    def get_expression(self, state_name: str) -> Dict[str, Any]:
        """Returns the expression manifest for a given PresenceState name."""
        # Fallback to an empty definition if not found
        default_expr = {
            "id": "unknown",
            "interruptible": True,
            "minimum_duration": 0,
            "outputs": {
                "visual": {"animation": "dim_glow"},
                "audio": {},
                "servo": {}
            }
        }
        return self.expressions.get(state_name.upper(), default_expr)
