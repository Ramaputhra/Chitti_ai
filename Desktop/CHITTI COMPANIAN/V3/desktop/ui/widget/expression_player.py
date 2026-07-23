import logging
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QPixmap
from desktop.ui.widget.animation_cache import AnimationCache

logger = logging.getLogger(__name__)

class ExpressionPlayer(QObject):
    frame_updated = Signal(QPixmap)
    
    def __init__(self, cache: AnimationCache):
        super().__init__()
        self.cache = cache
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        self.current_animation = "Idle"
        self.previous_state_animation = "Idle"
        self.frame_index = 0
        self.is_event = False
        
    def play_animation(self, animation_name: str, is_event: bool = False):
        if not self.cache.get_frames(animation_name):
            logger.warning(f"Animation folder missing for '{animation_name}', falling back to 'Idle'")
            animation_name = "Idle"
            is_event = False
            
        if self.current_animation == animation_name and not self.is_event and not is_event:
            return
            
        logger.info(f"Expression Transition: {self.current_animation} -> {animation_name}")
        
        self.timer.stop()
        
        if is_event:
            if not self.is_event:
                self.previous_state_animation = self.current_animation
        else:
            self.previous_state_animation = animation_name
            
        self.current_animation = animation_name
        self.is_event = is_event
        self.frame_index = 0
        
        meta = self.cache.get_metadata(animation_name)
        fps = meta.fps if meta else 24
        
        self.update_frame()
        self.timer.start(1000 // fps)
        
    def update_frame(self):
        frames = self.cache.get_frames(self.current_animation)
        if not frames:
            return
            
        if self.frame_index >= len(frames):
            self.frame_index = len(frames) - 1 # Clamp index to avoid out of bounds
            
        pixmap = frames[self.frame_index]
        self.frame_updated.emit(pixmap)
        
        self.frame_index += 1
        
        if self.frame_index >= len(frames):
            meta = self.cache.get_metadata(self.current_animation)
            loop = meta.loop if meta else True
            
            if self.is_event:
                self.play_animation(self.previous_state_animation, is_event=False)
            elif loop:
                self.frame_index = 0
            else:
                self.timer.stop()
