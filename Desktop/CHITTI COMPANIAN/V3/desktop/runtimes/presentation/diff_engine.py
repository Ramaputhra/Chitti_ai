import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from desktop.models.presentation import (
    PresentationModel, PresentationPatch, PatchOperation
)

class IDiffStrategy(ABC):
    """
    Abstract strategy for computing visual differences between two PresentationModels.
    """
    @abstractmethod
    def generate_patches(self, previous: PresentationModel, current: PresentationModel) -> List[PresentationPatch]:
        pass

class StructuralDiffStrategy(IDiffStrategy):
    """
    Base strategy for generating structural patches.
    Currently stubbed out. Will eventually perform deep dict diffing.
    """
    def generate_patches(self, previous: PresentationModel, current: PresentationModel) -> List[PresentationPatch]:
        # Rule 318: The DiffEngine exclusively generates patches. Capabilities never do.
        
        # Stub: If models differ, just return a single generic UPDATE_DATA patch.
        # In the future, this will recurse through the tree and emit specific ADD/REMOVE/UPDATE_STYLE patches.
        if previous.data != current.data:
            return [
                PresentationPatch(
                    patch_id=f"patch_{uuid.uuid4().hex[:6]}",
                    target_widget_id="root",
                    operation=PatchOperation.UPDATE_DATA,
                    diff_data=current.data
                )
            ]
        return []

class PresentationDiffEngine:
    """
    Compares consecutive PresentationModels to generate rendering patches.
    Insulates capabilities from knowing about DOM or HTML updates.
    """
    def __init__(self, strategy: Optional[IDiffStrategy] = None):
        self.strategy = strategy or StructuralDiffStrategy()
        
    def compute_diff(self, previous: PresentationModel, current: PresentationModel) -> List[PresentationPatch]:
        """
        Executes the configured diff strategy.
        """
        return self.strategy.generate_patches(previous, current)
