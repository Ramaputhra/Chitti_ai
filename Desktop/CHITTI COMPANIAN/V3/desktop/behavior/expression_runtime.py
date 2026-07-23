from abc import ABC, abstractmethod
from typing import List, Optional
from desktop.behavior.emotion_models import EmotionSnapshot
from desktop.behavior.character_models import FinalDialogue
from desktop.behavior.expression_models import AnimationDescriptor, AnimationLayer

class IAnimationAssetManager(ABC):
    @abstractmethod
    def resolve_asset(self, descriptor: AnimationDescriptor) -> str:
        """
        Maps semantic animation descriptors to physical assets (MP4, SpriteSheet, etc.).
        Expression Runtime remains ignorant of file extensions and renderer mechanics.
        """
        pass

class IAnimationBlender(ABC):
    @abstractmethod
    def push_animation(self, descriptor: AnimationDescriptor):
        """
        Evaluates the AnimationPolicy (e.g. STACKABLE, QUEUE, REPLACE) 
        and InterruptLevel. Pushes the animation into the appropriate layer stack.
        """
        pass
        
    @abstractmethod
    def pop_animation(self, layer: AnimationLayer):
        """
        Pops the top animation from the layer stack, resuming the previous animation 
        (e.g., popping 'Smile' resumes 'Thinking').
        """
        pass

class IExpressionRuntime(ABC):
    """
    The final visual renderer pipeline. Absorbs EmotionSnapshots (for BASE layer) 
    and FinalDialogue hints (for transient FACE/GESTURE layers), pushing them 
    into the AnimationBlender.
    """
    @abstractmethod
    async def start(self): pass
    
    @abstractmethod
    async def stop(self): pass
    
    @abstractmethod
    async def process_emotion_snapshot(self, snapshot: EmotionSnapshot):
        pass
        
    @abstractmethod
    async def process_dialogue_hints(self, dialogue: FinalDialogue):
        pass
