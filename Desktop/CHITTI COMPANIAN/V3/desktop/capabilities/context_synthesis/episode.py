from typing import Optional
from desktop.capabilities.context_synthesis.models import DesktopContextModel, ContextDiff

class ContextEpisodeDetector:
    """
    Detects meaningful semantic shifts in the DesktopContextModel.
    Filters out noise before pushing to the Memory Runtime.
    """
    def __init__(self):
        self.previous_context: Optional[DesktopContextModel] = None

    def evaluate_change(self, current_context: DesktopContextModel) -> tuple[bool, Optional[ContextDiff]]:
        if not self.previous_context:
            self.previous_context = current_context
            return True, None
            
        task_changed = current_context.current_task.value != self.previous_context.current_task.value
        project_changed = current_context.current_project.value != self.previous_context.current_project.value
        intent_changed = current_context.user_work_intent.value != self.previous_context.user_work_intent.value
        
        # Working set changes (e.g. opened a new file)
        working_set_changes = {}
        if current_context.working_set.value.active_files != self.previous_context.working_set.value.active_files:
            working_set_changes["files"] = current_context.working_set.value.active_files
            
        is_meaningful = task_changed or project_changed or intent_changed or bool(working_set_changes)
        
        diff = None
        if is_meaningful:
            diff = ContextDiff(
                previous_timestamp=self.previous_context.timestamp,
                current_timestamp=current_context.timestamp,
                task_changed=task_changed,
                intent_changed=intent_changed,
                project_changed=project_changed,
                working_set_changes=working_set_changes,
                summary_of_change="User context shifted to new task." if task_changed else "Working set updated."
            )
            
        self.previous_context = current_context
        return is_meaningful, diff
