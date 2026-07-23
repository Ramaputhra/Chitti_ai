import logging
from typing import Optional, Callable, Dict, Any
from desktop.character.presence.presence_events import PresenceStateEnum
from desktop.character.presence.presence_state_machine import PresenceStateMachine
from desktop.character.presence.presence_memory import PresenceMemory, RuntimeSessionModel
from desktop.character.presence.hotkey_listener import HotkeyListener
from desktop.character.presence.system_tray_manager import SystemTrayManager
from desktop.character.presence.desktop_context_manager import DesktopContextManager
from desktop.character.presence.conversation_state import ConversationStateEnum, ConversationContext

logger = logging.getLogger(__name__)

class CharacterPresenceController:
    """
    S36B-R2-R2: Master Character Presence Lifecycle Controller facade.
    Refined with Explicit Schema Versioning, Session-Centric Restoration, and Input Source Tracking.
    Visual presence visibility SHALL NEVER determine capability execution or background task processing.
    """
    def __init__(self, memory_path: Optional[str] = None):
        self.state_machine = PresenceStateMachine(initial_state=PresenceStateEnum.SYSTEM_TRAY)
        self.memory = PresenceMemory(storage_path=memory_path)
        self.hotkey_listener = HotkeyListener(shortcut="Ctrl+Space")
        self.tray_manager = SystemTrayManager()
        self.desktop_context_manager = DesktopContextManager(self.memory)
        self.conversation_context = ConversationContext()
        
        self.speech_active = False
        self.narration_active = False
        self.background_tasks_active = True
        self.wake_engine_active = True

        self.hotkey_listener.start_listening(callback=self._on_hotkey_triggered)
        logger.info(f"[CharacterPresenceController] Character Presence Lifecycle (S36B-R2-R2 Final Freeze) initialized. Memory Schema v{self.memory.data.presence_memory_version}")

    @property
    def current_state(self) -> PresenceStateEnum:
        return self.state_machine.current_state

    def wake_up(self, source: str = "wake_word", input_mode: str = "Wake Word"):
        logger.info(f"[CharacterPresenceController] Waking up via '{source}' (Mode: '{input_mode}') from state '{self.current_state.value}'")
        self.memory.data.last_wake_source = source
        self.memory.update_input_mode(input_mode)

        if self.current_state == PresenceStateEnum.SYSTEM_TRAY:
            self.state_machine.transition_to(PresenceStateEnum.WAKE)
            self.state_machine.transition_to(PresenceStateEnum.CHARACTER_WINDOW)
            logger.info(f"[CharacterPresenceController] Restored Character Window to ({self.memory.data.last_position_x}, {self.memory.data.last_position_y}) docked {self.memory.data.last_dock_edge}")
        elif self.current_state == PresenceStateEnum.PRESENCE_DOT:
            self.state_machine.transition_to(PresenceStateEnum.WAKE)
            self.state_machine.transition_to(PresenceStateEnum.CHARACTER_WINDOW)
            logger.info("[CharacterPresenceController] Expanded Presence Dot to Character Window. Conversation state preserved.")

    def restore_active_session(self) -> Dict[str, Any]:
        """
        Session-Centric Restoration: Restores the active runtime session from memory.
        """
        sess = self.memory.data.active_runtime_session
        logger.info(f"[CharacterPresenceController] Restoring Active Runtime Session '{sess.get('session_id')}' ({sess.get('runtime_type')})")
        return {
            "status": "RESTORED",
            "session": sess,
            "message": f"Runtime session '{sess.get('session_id')}' ({sess.get('runtime_type')}) restored cleanly."
        }

    def handle_first_middle_click(self):
        """
        Middle-click on Character Window: Transforms to Presence Dot.
        Speech & Narration CONTINUE uninterrupted.
        """
        if self.current_state == PresenceStateEnum.CHARACTER_WINDOW:
            self.memory.update_input_mode("Character Window")
            logger.info("[CharacterPresenceController] First Middle-Click: Transforming Character Window -> Presence Dot. Speech & Narration CONTINUE uninterrupted.")
            self.state_machine.transition_to(PresenceStateEnum.PRESENCE_DOT)

    def handle_second_middle_click(self):
        """
        Middle-click on Presence Dot: Transforms conversation state to PAUSED_BY_USER.
        Stops speech & narration immediately.
        Returns visual presence to System Tray while background tasks continue normally.
        """
        if self.current_state == PresenceStateEnum.PRESENCE_DOT:
            self.memory.update_input_mode("Presence Dot")
            logger.info("[CharacterPresenceController] Second Middle-Click: Pausing conversation (PAUSED_BY_USER). Returning to System Tray.")
            self.conversation_context.pause_by_user("User middle-clicked Presence Dot")
            self.speech_active = False
            self.narration_active = False
            self.memory.data.last_conversation_state = self.conversation_context.state.value
            self.memory.save()
            self.state_machine.transition_to(PresenceStateEnum.SYSTEM_TRAY)

    def request_conversation_resume(self) -> Dict[str, Any]:
        if self.conversation_context.state != ConversationStateEnum.PAUSED_BY_USER:
            return {"status": "NO_PAUSED_CONVERSATION", "message": "No active conversation is currently paused by user."}

        if self.conversation_context.resume_allowed:
            ok = self.conversation_context.resume()
            if ok:
                self.speech_active = True
                self.narration_active = True
                self.memory.data.last_conversation_state = self.conversation_context.state.value
                self.memory.save()
                return {
                    "status": "RESUMED",
                    "narration_offset": self.conversation_context.narration_offset,
                    "speech_offset": self.conversation_context.speech_offset,
                    "message": f"Resuming previous explanation from step {self.conversation_context.narration_offset}..."
                }

        return {
            "status": "NOT_RESUMABLE",
            "message": f"The capability '{self.conversation_context.current_capability}' cannot be resumed from where it stopped. Would you like me to restart it from the beginning or summarize instead?"
        }

    def enter_presentation_mode(self):
        if self.current_state == PresenceStateEnum.CHARACTER_WINDOW:
            self.memory.update_input_mode("Presentation Controller")
            self.desktop_context_manager.enter_presentation(
                current_x=self.memory.data.last_position_x,
                current_y=self.memory.data.last_position_y,
                current_dock=self.memory.data.last_dock_edge,
                current_scale=self.memory.data.last_window_scale
            )
            self.conversation_context.state = ConversationStateEnum.ACTIVE
            self.state_machine.transition_to(PresenceStateEnum.PRESENCE_DOT)

    def exit_presentation_mode(self):
        saved = self.desktop_context_manager.exit_presentation()
        self.state_machine.transition_to(PresenceStateEnum.CHARACTER_WINDOW)
        logger.info(f"[CharacterPresenceController] Restored Character Window to pre-presentation state: {saved}")

    def _on_hotkey_triggered(self):
        logger.info("[CharacterPresenceController] Global Hotkey triggered callback.")
        self.wake_up(source="global_hotkey", input_mode="Global Hotkey")
