"""
VIZZU Animation Orchestrator
===========================
Manages all avatar animations based on the voice command flow:
Listening → Performing Task → Success → Idle

Implements idle timers, stretch animations, and system tray transitions.
"""

import asyncio
import logging
import random
from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass
from threading import Timer

from desktop.models.audio_models import SpeechState

logger = logging.getLogger(__name__)


class AnimationCategory(Enum):
    """Categories of animations in the system"""
    SYSTEM = "system"
    SPEECH = "speech"
    EXECUTION = "execution"
    RESULT = "result"
    IDLE = "idle"
    TALKING = "talking"


@dataclass
class AnimationConfig:
    """Configuration for a single animation"""
    name: str
    category: AnimationCategory
    duration_ms: int
    loop: bool = False
    interruptible: bool = True
    sprite_frames: int = 14


class IdleState(Enum):
    """States for idle timer management"""
    ACTIVE = "active"  # User is interacting
    IDLE_0_60s = "idle_0_60s"  # 0-60 seconds idle
    IDLE_60_120s = "idle_60_120s"  # 60-120 seconds idle
    IDLE_DOT = "idle_dot"  # Minimized to system tray


class AnimationOrchestrator:
    """
    Central orchestrator for all avatar animations.
    
    Manages:
    - Speech state to animation mapping
    - Task execution animations
    - Idle timers and stretch animations
    - System tray (dot) transitions
    - Intro animation variants
    """
    
    # Animation Registry - maps states/intents to animation configs
    ANIMATIONS = {
        # === SYSTEM ANIMATIONS ===
        "boot_start": AnimationConfig("boot_start", AnimationCategory.SYSTEM, 1500),
        "boot_progress": AnimationConfig("boot_progress", AnimationCategory.SYSTEM, 2000, loop=True),
        "boot_complete": AnimationConfig("boot_complete", AnimationCategory.SYSTEM, 1000),
        "idle_to_dot": AnimationConfig("idle_to_dot", AnimationCategory.SYSTEM, 2000),
        "dot_idle": AnimationConfig("dot_idle", AnimationCategory.SYSTEM, 0, loop=True),
        "intro_from_dot_1": AnimationConfig("intro_from_dot_1", AnimationCategory.SYSTEM, 1500),
        "intro_from_dot_2": AnimationConfig("intro_from_dot_2", AnimationCategory.SYSTEM, 1500),
        "intro_from_dot_3": AnimationConfig("intro_from_dot_3", AnimationCategory.SYSTEM, 1500),
        "stretch_1min": AnimationConfig("stretch_1min", AnimationCategory.SYSTEM, 500),
        "stretch_2min": AnimationConfig("stretch_2min", AnimationCategory.SYSTEM, 800),
        "goodbye": AnimationConfig("goodbye", AnimationCategory.SYSTEM, 2000),
        "shutdown": AnimationConfig("shutdown", AnimationCategory.SYSTEM, 1500),
        
        # === SPEECH/LISTENING ANIMATIONS ===
        "wake_detected": AnimationConfig("wake_detected", AnimationCategory.SPEECH, 500),
        "listening_active": AnimationConfig("listening_active", AnimationCategory.SPEECH, 1000, loop=True),
        "listening_pulse": AnimationConfig("listening_pulse", AnimationCategory.SPEECH, 300, loop=True),
        "processing_command": AnimationConfig("processing_command", AnimationCategory.SPEECH, 800),
        "understanding": AnimationConfig("understanding", AnimationCategory.SPEECH, 500),
        
        # === TASK EXECUTION ANIMATIONS ===
        "executing_general": AnimationConfig("executing_general", AnimationCategory.EXECUTION, 1000, loop=True),
        "executing_file": AnimationConfig("executing_file", AnimationCategory.EXECUTION, 1000, loop=True),
        "executing_browser": AnimationConfig("executing_browser", AnimationCategory.EXECUTION, 1000, loop=True),
        "executing_app": AnimationConfig("executing_app", AnimationCategory.EXECUTION, 1000, loop=True),
        "executing_calendar": AnimationConfig("executing_calendar", AnimationCategory.EXECUTION, 1000, loop=True),
        "executing_clipboard": AnimationConfig("executing_clipboard", AnimationCategory.EXECUTION, 500, loop=True),
        "executing_search": AnimationConfig("executing_search", AnimationCategory.EXECUTION, 1000, loop=True),
        "executing_system": AnimationConfig("executing_system", AnimationCategory.EXECUTION, 1000, loop=True),
        
        # === RESULT ANIMATIONS ===
        "task_success": AnimationConfig("task_success", AnimationCategory.RESULT, 1500),
        "task_partial": AnimationConfig("task_partial", AnimationCategory.RESULT, 1200),
        "task_failed": AnimationConfig("task_failed", AnimationCategory.RESULT, 1500),
        "task_blocked": AnimationConfig("task_blocked", AnimationCategory.RESULT, 1000),
        "waiting_for_confirm": AnimationConfig("waiting_for_confirm", AnimationCategory.RESULT, 1000, loop=True),
        "confirming": AnimationConfig("confirming", AnimationCategory.RESULT, 800),
        
        # === TALKING ANIMATIONS ===
        "talking": AnimationConfig("talking", AnimationCategory.TALKING, 1000, loop=True),
        "talking_short": AnimationConfig("talking_short", AnimationCategory.TALKING, 500, loop=True),
        "talking_explain": AnimationConfig("talking_explain", AnimationCategory.TALKING, 1500, loop=True),
        
        # === IDLE ANIMATIONS ===
        "idle_normal": AnimationConfig("idle_normal", AnimationCategory.IDLE, 0, loop=True),
        "idle_happy": AnimationConfig("idle_happy", AnimationCategory.IDLE, 0, loop=True),
        "idle_curious": AnimationConfig("idle_curious", AnimationCategory.IDLE, 0, loop=True),
        "idle_waiting": AnimationConfig("idle_waiting", AnimationCategory.IDLE, 0, loop=True),
        "idle_blink": AnimationConfig("idle_blink", AnimationCategory.IDLE, 200, loop=True),
    }
    
    # Idle timer thresholds (in seconds)
    IDLE_STRETCH_1_THRESHOLD = 60  # 1 minute
    IDLE_STRETCH_2_THRESHOLD = 120  # 2 minutes
    IDLE_DOT_THRESHOLD = 120  # 2 minutes to minimize
    
    def __init__(self, event_bus, expression_callback: Callable[[str], None]):
        """
        Initialize the animation orchestrator.
        
        Args:
            event_bus: Event bus for subscribing to system events
            expression_callback: Callback function to trigger actual animation playback
        """
        self.event_bus = event_bus
        self.expression_callback = expression_callback
        
        self.current_animation: Optional[str] = None
        self.current_state = IdleState.ACTIVE
        self._idle_timer: Optional[Timer] = None
        self._idle_seconds = 0
        self._is_minimized = False
        self._intro_variant_used = 0
        
        # Subscribe to relevant events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to system events for animation triggers"""
        if hasattr(self.event_bus, 'subscribe'):
            self.event_bus.subscribe("SPEECH_STATE_CHANGED", self._on_speech_state_changed)
            self.event_bus.subscribe("TASK_STARTED", self._on_task_started)
            self.event_bus.subscribe("TASK_COMPLETED", self._on_task_completed)
            self.event_bus.subscribe("TASK_FAILED", self._on_task_failed)
            self.event_bus.subscribe("USER_GOODBYE", self._on_user_goodbye)
            self.event_bus.subscribe("SYSTEM_WAKE", self._on_system_wake)
            self.event_bus.subscribe("IDLE_TICK", self._on_idle_tick)
    
    def _on_speech_state_changed(self, event):
        """Map speech states to animations"""
        payload = event.get('payload', {}) if isinstance(event, dict) else getattr(event, 'payload', {})
        state = payload.get('state', '')
        
        state_animation_map = {
            'WAKE_DETECTED': 'wake_detected',
            'LISTENING': 'listening_active',
            'UNDERSTANDING': 'understanding',
            'THINKING': 'processing_command',
            'EXPECTING_REPLY': 'waiting_for_confirm',
            'SLEEPING': 'idle_normal',
        }
        
        animation = state_animation_map.get(state)
        if animation:
            self.play(animation)
    
    def _on_task_started(self, event):
        """Start task execution animation"""
        payload = event.get('payload', {}) if isinstance(event, dict) else getattr(event, 'payload', {})
        task_type = payload.get('task_type', 'general')
        
        animation = f"executing_{task_type}"
        if animation not in self.ANIMATIONS:
            animation = "executing_general"
        
        self.play(animation)
        self._reset_idle_timer()
    
    def _on_task_completed(self, event):
        """Play success animation after task completion"""
        payload = event.get('payload', {}) if isinstance(event, dict) else getattr(event, 'payload', {})
        status = payload.get('status', 'success')
        
        animation_map = {
            'success': 'task_success',
            'partial': 'task_partial',
            'failed': 'task_failed',
        }
        
        animation = animation_map.get(status, 'task_success')
        self.play(animation)
    
    def _on_task_failed(self, event):
        """Play failure animation"""
        self.play('task_failed')
    
    def _on_user_goodbye(self, event):
        """Handle user saying goodbye"""
        self.play('goodbye')
        # After goodbye animation, minimize to dot
        asyncio.create_task(self._delayed_minimize())
    
    def _on_system_wake(self, event):
        """Handle wake from system tray"""
        if self._is_minimized:
            self._is_minimized = False
            # Play random intro variant
            variant = random.randint(1, 3)
            self.play(f'intro_from_dot_{variant}')
            self._intro_variant_used = variant
    
    def _on_idle_tick(self, event):
        """Handle idle timer ticks"""
        payload = event.get('payload', {}) if isinstance(event, dict) else getattr(event, 'payload', {})
        seconds = payload.get('seconds', 0)
        
        self._idle_seconds = seconds
        
        if seconds >= self.IDLE_STRETCH_2_THRESHOLD and not self._is_minimized:
            self.play('idle_to_dot')
            asyncio.create_task(self._delayed_minimize())
        elif seconds >= self.IDLE_STRETCH_1_THRESHOLD:
            self.play('stretch_1min')
    
    async def _delayed_minimize(self):
        """Delay before minimizing to system tray"""
        await asyncio.sleep(2)  # Wait for animation to complete
        self._is_minimized = True
        self.play('dot_idle')
        self._cancel_idle_timer()
    
    def _reset_idle_timer(self):
        """Reset idle timer on user activity"""
        self._idle_seconds = 0
        self.current_state = IdleState.ACTIVE
        if self._idle_timer:
            self._idle_timer.cancel()
    
    def _cancel_idle_timer(self):
        """Cancel the idle timer"""
        if self._idle_timer:
            self._idle_timer.cancel()
            self._idle_timer = None
    
    def play(self, animation_name: str):
        """
        Play an animation.
        
        Args:
            animation_name: Name of the animation to play
        """
        if animation_name not in self.ANIMATIONS:
            logger.warning(f"Animation not found: {animation_name}")
            return
        
        config = self.ANIMATIONS[animation_name]
        self.current_animation = animation_name
        
        logger.info(f"AnimationOrchestrator: Playing {animation_name} ({config.category.value})")
        
        # Call the expression callback to trigger actual animation
        if self.expression_callback:
            self.expression_callback(animation_name)
    
    def play_for_speech(self, speech_duration_ms: int):
        """
        Play talking animation for the duration of speech.
        
        Args:
            speech_duration_ms: Duration of the speech in milliseconds
        """
        if speech_duration_ms > 2000:
            self.play('talking_explain')
        else:
            self.play('talking_short')
    
    def get_animation_for_capability(self, capability_type: str) -> str:
        """
        Get the appropriate animation for a capability type.
        
        Args:
            capability_type: Type of capability being executed
            
        Returns:
            Animation name to play
        """
        type_map = {
            'file': 'executing_file',
            'folder': 'executing_file',
            'browser': 'executing_browser',
            'web': 'executing_browser',
            'app': 'executing_app',
            'application': 'executing_app',
            'calendar': 'executing_calendar',
            'reminder': 'executing_calendar',
            'timer': 'executing_calendar',
            'clipboard': 'executing_clipboard',
            'copy': 'executing_clipboard',
            'paste': 'executing_clipboard',
            'search': 'executing_search',
            'find': 'executing_search',
            'system': 'executing_system',
            'settings': 'executing_system',
        }
        
        return type_map.get(capability_type.lower(), 'executing_general')
    
    def get_idle_animation(self, mood: str = 'normal') -> str:
        """
        Get the appropriate idle animation based on mood.
        
        Args:
            mood: Idle mood - 'normal', 'happy', 'curious', 'waiting'
            
        Returns:
            Idle animation name
        """
        mood_map = {
            'normal': 'idle_normal',
            'happy': 'idle_happy',
            'curious': 'idle_curious',
            'waiting': 'idle_waiting',
        }
        
        return mood_map.get(mood, 'idle_normal')
    
    def set_idle_mood(self, mood: str):
        """Change the idle mood (only affects when idle)"""
        if self.current_state in [IdleState.IDLE_0_60s, IdleState.IDLE_60_120s]:
            self.play(self.get_idle_animation(mood))


class IdleAnimationManager:
    """
    Manages idle animations and timers.
    Runs independently from main animation orchestrator.
    """
    
    def __init__(self, orchestrator: AnimationOrchestrator):
        self.orchestrator = orchestrator
        self._timer_task: Optional[asyncio.Task] = None
        self._running = False
        self._idle_seconds = 0
    
    async def start(self):
        """Start the idle animation manager"""
        self._running = True
        self._timer_task = asyncio.create_task(self._idle_loop())
        logger.info("IdleAnimationManager started")
    
    async def stop(self):
        """Stop the idle animation manager"""
        self._running = False
        if self._timer_task:
            self._timer_task.cancel()
        logger.info("IdleAnimationManager stopped")
    
    async def _idle_loop(self):
        """Main idle timer loop"""
        while self._running:
            await asyncio.sleep(1)  # Tick every second
            
            # Publish idle tick event
            if hasattr(self.orchestrator.event_bus, 'publish'):
                from desktop.platform.shared.interfaces.event_bus import Event
                self.orchestrator.event_bus.publish(Event(
                    event_type="IDLE_TICK",
                    source="IdleAnimationManager",
                    payload={"seconds": self._idle_seconds}
                ))
            
            self._idle_seconds += 1
    
    def reset(self):
        """Reset idle timer on user activity"""
        self._idle_seconds = 0
    
    @property
    def idle_time(self) -> int:
        """Get current idle time in seconds"""
        return self._idle_seconds
