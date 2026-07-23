import sys
import os
import time
import logging
import signal

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, v3_root)

from PySide6.QtWidgets import QApplication
from desktop.platform.integrations.core.event_bus import EventBus
from desktop.services.audio.providers.piper_provider import PiperProvider
from desktop.services.audio.providers.faster_whisper_provider import FasterWhisperProvider
from desktop.platform.integrations.core.provider_registry import SpeechSynthRegistry
from desktop.services.audio.speech_synth_router import SpeechSynthRouter
from desktop.runtimes.expression.outputs.voice.runtime import VoiceRuntime
from desktop.runtimes.expression.outputs.voice.events import SpeakRequested
from desktop.runtimes.audio.input.runtime import AudioInputRuntime
from desktop.platform.ai.speech_orchestrator import SpeechOrchestrator
from desktop.ui.presence.presence_engine import PresenceEngine
from desktop.runtimes.expression.runtime import ExpressionRuntime
from desktop.ui.widget.companion_widget import CompanionWidget

from desktop.platform.ai.conversation_logger import ConversationLogger
from desktop.platform.integrations.core.provider_registry import LLMProviderRegistry
from desktop.runtimes.inference.runtime import InferenceRuntime
from desktop.platform.ai.semantic_runtime import SemanticRuntime
from desktop.services.skills.skill_registry import SkillRegistry
from desktop.services.language.capability_resolver import CapabilityResolver
from desktop.runtimes.capability.runtime import CapabilityRuntime
from desktop.runtimes.conversation.runtime import ConversationRuntime
from desktop.runtimes.ai.runtime import AIRuntime
from desktop.runtimes.planner import PlannerRuntime
from desktop.runtimes.execution import ExecutionRuntime
from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
from desktop.app.context import KernelContext
from desktop.platform.integrations.core.registry import ServiceRegistry
from desktop.app.memory_contracts import IMemoryService
from desktop.platform.core.experience_repository import ExperienceRepository
from desktop.platform.core.session_context import SessionContext
from desktop.runtimes.conversation.session_runtime import ConversationSessionRuntime
from desktop.ui.widget.chat_workspace import ChatWorkspace
from desktop.runtimes.experience.runtime import ExperienceRuntime
from desktop.models.execution_models import WorkflowVerifiedEvent, ExecutionStatus
from desktop.capabilities.application_launch.skill import ApplicationLaunchSkill

class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARN: {msg}")
    def debug(self, msg): pass
    def event(self, event_id, **kwargs): pass
    def exception(self, e, **kwargs): print(f"EXC: {e}")


def main():
    logging.basicConfig(level=logging.INFO)
    print("=== CHITTI VOICE INPUT PREVIEW ===")
    
    # Allow Ctrl+C to kill the PySide6 app from the terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    
    mlogger = MockLogger()
    event_bus = EventBus(logger=mlogger)
    event_bus.start()
    
    # 1. Output (Piper & VoiceRuntime)
    piper = PiperProvider(event_bus=event_bus, logger=mlogger)
    piper.load_model(r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper\en_US-amy-medium.onnx")
    
    registry = SpeechSynthRegistry(logger=mlogger)
    registry.register_provider(piper)
    router = SpeechSynthRouter(registry=registry, logger=mlogger)
    
    voice_runtime = VoiceRuntime(event_bus=event_bus, speech_router=router)
    voice_runtime.start()
    
    # 2. Input (OpenWakeWord, Faster-Whisper, AudioInputRuntime)
    audio_input = AudioInputRuntime(event_bus=event_bus)
    audio_input.start()
    
    whisper = FasterWhisperProvider(event_bus=event_bus, logger=mlogger)
    whisper.load_model("small") # Use small for fast local multilingual inference
    
    # 3. Orchestration
    orchestrator = SpeechOrchestrator(event_bus=event_bus)
    
    # 4. Intelligence & Orchestration
    conv_logger = ConversationLogger(event_bus=event_bus)
    
    # Session Runtime
    session_context = SessionContext(conversation_id="")
    session_runtime = ConversationSessionRuntime(event_bus=event_bus, session_context=session_context)
    session_runtime.start()
    
    # Experience Engine
    experience_repository = ExperienceRepository()
    experience_runtime = ExperienceRuntime(event_bus=event_bus, repository=experience_repository)
    experience_runtime.start()
    
    semantic_runtime = SemanticRuntime(event_bus=event_bus, experience_repository=experience_repository)
    
    # Connect to inference registry (which inherently creates LlamaCppProvider)
    llm_registry = LLMProviderRegistry(logger=mlogger)
    
    inference_runtime = InferenceRuntime(event_bus=event_bus, registry=llm_registry)
    inference_runtime.start()
    
    # We retrieve the provider strictly for the mock orchestrator below
    gguf_llm = llm_registry.get_active_providers()[0]
    
    skill_registry = SkillRegistry(logger=mlogger)
    skill_registry.register(ApplicationLaunchSkill())
    
    capability_resolver = CapabilityResolver(skill_registry=skill_registry, logger=mlogger)
    capability_runtime = CapabilityRuntime(resolver=capability_resolver, event_bus=event_bus)
    
    ai_runtime = AIRuntime(inference_runtime=inference_runtime)
    ai_runtime.start()
    
    conversation_runtime = ConversationRuntime(event_bus=event_bus)
    conversation_runtime.start()
    
    # --- TRUE EXECUTION PIPELINE ---
    
    # 1. Instantiate Core Dependencies for Runtimes
    class MockMemoryService(IMemoryService):
        def append_interaction(self, session_id, interaction_id, role, content, metadata=None): pass
        def append_episode(self, session_id, episode_id, goal, summary, metrics=None): pass
        def snapshot(self, session_id, workflow_id=None): return None

    registry = ServiceRegistry()
    registry.register(IMemoryService, MockMemoryService())
    kernel_context = KernelContext(event_bus=event_bus, registry=registry)
    
    # 2. Planner (Replaces Mock Orchestrator)
    planner_strategy = DeterministicPlannerStrategy()
    planner_runtime = PlannerRuntime(planner_strategy)
    planner_runtime.context = kernel_context
    planner_runtime.start()
    
    # Subscribe Planner to Conversational Input
    from desktop.models.interaction import InteractionEnvelope
    event_bus.subscribe(InteractionEnvelope, lambda ev: import_asyncio().create_task(planner_runtime.process_intent(ev.payload if hasattr(ev, 'payload') else ev)))
    
    def import_asyncio():
        import asyncio
        return asyncio
    
    # 3. Execution (Executes the Plans produced by Planner)
    from desktop.platform.integrations.core.registry import SimpleCapabilityRegistry
    from desktop.packages.productivity_workspace_pack.capabilities.resume_activity import ResumeActivityCapability
    from desktop.app.capability_contracts import CapabilityDescriptor as CoreCapabilityDescriptor
    
    cap_registry = SimpleCapabilityRegistry()
    
    # Register ResumeActivityCapability
    cap = ResumeActivityCapability()
    cap_descriptor = CoreCapabilityDescriptor(
        id="ResumeActivityCapability", 
        version="1.0", 
        permissions=["workspace", "execution"], 
        execution_mode="sync", 
        factory=lambda: cap
    )
    cap_registry.register(cap_descriptor)
    
    execution_runtime = ExecutionRuntime(cap_registry)
    execution_runtime.context = kernel_context
    execution_runtime.initialize(kernel_context) # This subscribes it to ExecutionPlan
    execution_runtime.start()
    
    # --- END TRUE PIPELINE ---
    
    # 5. Avatar & Presence
    presence_engine = PresenceEngine(event_bus)
    presence_engine.start()
    
    expr_runtime = ExpressionRuntime(event_bus)
    expr_runtime.start()
    
    companion = CompanionWidget()
    companion.show()
    
    chat_workspace = ChatWorkspace(event_bus=event_bus)
    chat_workspace.show()
    
    # Wire the background Expression events to the Main UI Thread
    from desktop.ui.widget.expression_controller import ExpressionController
    controller = ExpressionController(event_bus)
    controller.animation_started_signal.connect(companion.handle_expression_started)
    
    print("\n[System] Ready! Say 'Alexa' to wake, then ask a question.")
    print("Example: 'Alexa', [Wait for Listening Animation], 'What time is it?'")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
