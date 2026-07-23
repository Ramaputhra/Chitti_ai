from enum import Enum
from typing import Dict

class SemanticWindowLayer(Enum):
    CHARACTER = 100
    CHARACTER_WIDGET = 200
    FLOATING_WIDGET = 300
    NOTIFICATION = 400
    DIALOG = 500
    SYSTEM_OVERLAY = 600
    DEBUG = 700

class WindowLayerTranslator:
    """
    S36D-1-R1: Translates Semantic Window Layers into OS-specific Z-Order priorities.
    Ensures:
    - Character Window < Character Widgets
    - Character Widgets < Dialogs
    - Dialogs < System Overlays
    - Debug Windows < Topmost (Debug mode only)
    """
    @staticmethod
    def get_layer_priority(layer: SemanticWindowLayer) -> int:
        return layer.value

    @staticmethod
    def is_layer_above(layer1: SemanticWindowLayer, layer2: SemanticWindowLayer) -> bool:
        return layer1.value > layer2.value
