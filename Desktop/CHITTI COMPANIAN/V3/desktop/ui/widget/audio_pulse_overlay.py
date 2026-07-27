"""
VIZZU Audio Pulse Overlay
========================
Minimal glowing white audio pulse indicator at center-bottom of avatar.
Reacts to real-time audio incoming levels.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QRadialGradient


class AudioPulseOverlay(QWidget):
    """
    Minimal audio pulse indicator at center-bottom of avatar.
    
    Features:
    - White glowing pulse bar
    - Fades at left and right edges
    - Reacts to real-time audio levels
    - Smooth animations
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Pulse configuration
        self._width_ratio = 0.6  # 60% of parent width
        self._bottom_margin = 20  # pixels from bottom
        self._height = 4  # current pulse height
        self._target_height = 4  # target height for animation
        self._opacity = 0.7  # current opacity
        
        # Audio level state
        self._audio_level = 0.0  # 0.0 to 1.0
        self._is_listening = False
        self._is_idle = False
        
        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._timer.start(16)  # ~60 FPS
        
        # Idle pulse animation state
        self._idle_time = 0
        
    def set_audio_level(self, level: float):
        """
        Update pulse based on audio level.
        
        Args:
            level: Audio level from 0.0 (silent) to 1.0 (max)
        """
        self._audio_level = max(0.0, min(1.0, level))
        self._is_listening = True
        self._is_idle = False
        
        # Calculate target height based on audio level
        # Idle: 2px, Normal: 4px, Active: 4-12px
        if self._audio_level < 0.1:
            self._target_height = 2
            self._opacity = 0.3
        elif self._audio_level < 0.3:
            self._target_height = 4
            self._opacity = 0.5
        else:
            self._target_height = 4 + (self._audio_level * 8)
            self._opacity = 0.5 + (self._audio_level * 0.5)
        
        self.update()
    
    def set_listening(self, listening: bool = True):
        """
        Set listening state.
        
        Args:
            listening: True if actively listening
        """
        self._is_listening = listening
        self._is_idle = False
        
        if listening:
            self._timer.start()
        self.update()
    
    def set_idle(self):
        """Set to idle animation state with slow pulse."""
        self._is_idle = True
        self._is_listening = False
        self._audio_level = 0.0
        self._idle_time = 0
        self.update()
    
    def hide_pulse(self):
        """Hide the pulse completely."""
        self._is_listening = False
        self._is_idle = False
        self._opacity = 0.0
        self._height = 0
        self.update()
    
    def _update_animation(self):
        """Update pulse animation at 60 FPS."""
        if not self._is_idle:
            # Animate height towards target
            diff = self._target_height - self._height
            self._height += diff * 0.3  # Fast attack
        
        if self._is_idle:
            # Idle pulse animation (2 second cycle)
            self._idle_time += 16
            cycle = (self._idle_time % 2000) / 2000.0
            
            # Ease in-out
            import math
            self._opacity = 0.3 + (math.sin(cycle * 2 * math.pi) * 0.15)
            self._height = 2
        elif not self._is_listening:
            # Fade out when not listening
            self._opacity *= 0.95
            if self._opacity < 0.01:
                self._opacity = 0.0
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the audio pulse overlay."""
        if self._opacity < 0.01:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        parent_width = self.parent().width() if self.parent() else self.width()
        width = int(parent_width * self._width_ratio)
        height = max(1, int(self._height))
        
        # Center horizontally
        x = (self.width() - width) // 2
        # Position from bottom
        y = self.height() - self._bottom_margin - height
        
        # Ensure minimum visibility
        if self._opacity < 0.1:
            return
        
        # Draw glow layer (wider, more transparent)
        glow_height = height + 12
        glow_y = y - 6
        glow_gradient = QLinearGradient(x, 0, x + width, 0)
        glow_gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        glow_gradient.setColorAt(0.2, QColor(255, 255, 255, int(40 * self._opacity)))
        glow_gradient.setColorAt(0.5, QColor(255, 255, 255, int(100 * self._opacity)))
        glow_gradient.setColorAt(0.8, QColor(255, 255, 255, int(40 * self._opacity)))
        glow_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow_gradient)
        painter.drawRoundedRect(x, glow_y, width, glow_height, glow_height // 2)
        
        # Draw main pulse (white with edge fade)
        main_gradient = QLinearGradient(x, 0, x + width, 0)
        main_gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        main_gradient.setColorAt(0.15, QColor(255, 255, 255, int(150 * self._opacity)))
        main_gradient.setColorAt(0.5, QColor(255, 255, 255, int(255 * self._opacity)))
        main_gradient.setColorAt(0.85, QColor(255, 255, 255, int(150 * self._opacity)))
        main_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        
        painter.setBrush(main_gradient)
        painter.drawRoundedRect(x, y, width, height, height // 2)


class AudioPulseManager:
    """
    Manages audio pulse overlay lifecycle and audio level integration.
    """
    
    def __init__(self, event_bus, pulse_overlay: AudioPulseOverlay):
        self.event_bus = event_bus
        self.pulse = pulse_overlay
        self._audio_level = 0.0
        self._smoothing_factor = 0.3
        
        # Subscribe to events
        if hasattr(event_bus, 'subscribe'):
            event_bus.subscribe("AUDIO_LEVEL_UPDATE", self._on_audio_level)
            event_bus.subscribe("SPEECH_STARTED", self._on_speech_started)
            event_bus.subscribe("SPEECH_STOPPED", self._on_speech_stopped)
            event_bus.subscribe("LISTENING_ACTIVE", self._on_listening_active)
            event_bus.subscribe("SLEEPING", self._on_sleeping)
    
    def _on_audio_level(self, event):
        """Handle real-time audio level updates."""
        payload = event.get('payload', {}) if isinstance(event, dict) else getattr(event, 'payload', {})
        level = payload.get('level', 0.0)
        
        # Apply smoothing to prevent jittery animations
        self._audio_level = (self._audio_level * (1 - self._smoothing_factor) + 
                            level * self._smoothing_factor)
        
        self.pulse.set_audio_level(self._audio_level)
    
    def _on_speech_started(self, event):
        """Handle speech started event."""
        self.pulse.set_listening(True)
    
    def _on_speech_stopped(self, event):
        """Handle speech stopped event."""
        self.pulse.set_idle()
    
    def _on_listening_active(self, event):
        """Handle listening active event."""
        self.pulse.set_listening(True)
    
    def _on_sleeping(self, event):
        """Handle sleeping state - hide pulse."""
        self.pulse.hide_pulse()
    
    def update_from_vad(self, audio_data: bytes):
        """
        Update pulse from raw audio data (VAD callback).
        
        Args:
            audio_data: Raw audio bytes
        """
        if not audio_data:
            return
        
        # Calculate simple RMS level from audio data
        import struct
        
        # Assume 16-bit audio
        try:
            # Convert bytes to 16-bit integers
            samples = struct.unpack(f"{len(audio_data)//2}h", audio_data)
            
            # Calculate RMS
            import math
            rms = math.sqrt(sum(s * s for s in samples) / len(samples))
            
            # Normalize to 0-1 range (assuming 16-bit audio)
            level = min(1.0, rms / 16384.0)
            
            self.pulse.set_audio_level(level)
        except:
            pass
