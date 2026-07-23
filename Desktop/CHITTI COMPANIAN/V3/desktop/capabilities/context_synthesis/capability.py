from typing import Dict, Any, Optional
from desktop.capabilities.screen_understanding.models import ScreenModel
from desktop.capabilities.context_synthesis.models import (
    DesktopContextModel, ContextField, UserWorkIntent, WorkingSet
)
from desktop.capabilities.context_synthesis.extractors import (
    IDEExtractor, BrowserExtractor, MeetingExtractor
)
from desktop.capabilities.context_synthesis.episode import ContextEpisodeDetector

class ContextSynthesisCapability:
    """
    Synthesizes the World Runtime's latest ScreenModel into a rich DesktopContextModel.
    Implements Rule 131, 132, 133 (World Consumption, Synthesis Purity, Context Caching).
    """
    def __init__(self, world_runtime, ai_runtime):
        self.world_runtime = world_runtime
        self.ai_runtime = ai_runtime
        
        self.extractors = [
            IDEExtractor(),
            BrowserExtractor(),
            MeetingExtractor()
        ]
        
        self.episode_detector = ContextEpisodeDetector()
        
        # Cache for lazy evaluation (Rule 133)
        self._cached_context: Optional[DesktopContextModel] = None
        self._last_screen_timestamp = None

    async def execute(self, payload: Dict[str, Any]) -> DesktopContextModel:
        # 1. Consume from World Runtime (Rule 131)
        latest_screen_model: ScreenModel = self.world_runtime.get_latest_screen_model()
        
        # 2. Check Cache (Rule 133)
        if self._cached_context and latest_screen_model.timestamp == self._last_screen_timestamp:
            return self._cached_context
            
        # 3. Run extractors lazily based on application context
        extracted_data = {}
        for extractor in self.extractors:
            if extractor.supports(latest_screen_model):
                updates = extractor.extract(latest_screen_model)
                extracted_data.update(updates)
                
        # 4. Infer Task & Working Set using AI Runtime (Stubbed)
        # ai_inference = await self.ai_runtime.invoke_capability(...)
        current_task_inferred = "Implementing Context Synthesis Capability"
        inferred_intent = UserWorkIntent.IMPLEMENTING
        
        working_set = WorkingSet(
            active_files=["capability.py", "models.py"],
            recent_documents=["AGENTS.md"]
        )
        
        # 5. Build DesktopContextModel
        context = DesktopContextModel(
            current_task=ContextField(current_task_inferred, 0.95, ["ScreenModel", "IDE", "Git"]),
            user_work_intent=ContextField(inferred_intent, 0.90, ["ScreenModel", "ActivityHistory"]),
            current_project=extracted_data.get("current_project", ContextField("Unknown", 1.0, ["Default"])),
            current_document=ContextField(latest_screen_model.document, 1.0, ["ScreenModel"]),
            current_activity=ContextField("Coding", 0.98, ["ScreenModel"]),
            application_stack=ContextField([latest_screen_model.application], 1.0, ["ScreenModel"]),
            workspace=ContextField("CHITTI_Workspace", 1.0, ["Config"]),
            meeting=extracted_data.get("meeting", ContextField({"in_meeting": False}, 1.0, ["Default"])),
            coding_context=extracted_data.get("coding_context", ContextField(None, 1.0, ["Default"])),
            browser_context=extracted_data.get("browser_context", ContextField(None, 1.0, ["Default"])),
            working_set=ContextField(working_set, 0.92, ["IDE", "AI Inference"]),
            estimated_focus=ContextField(0.95, 0.8, ["ActivityHistory"])
        )
        
        # 6. Evaluate Episode
        is_meaningful, diff = self.episode_detector.evaluate_change(context)
        if is_meaningful:
            # Pushes diff to Memory Runtime here
            pass
            
        # Update Cache
        self._cached_context = context
        self._last_screen_timestamp = latest_screen_model.timestamp
        
        return context
