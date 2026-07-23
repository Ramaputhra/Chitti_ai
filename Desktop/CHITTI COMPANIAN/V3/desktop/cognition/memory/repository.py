from abc import ABC, abstractmethod
from typing import List
from desktop.models.identity import ProjectIdentity
from desktop.models.cognition import Goal

class GoalRepository(ABC):
    @abstractmethod
    def get_recent_goals(self, project: ProjectIdentity) -> List[Goal]:
        pass
        
    @abstractmethod
    def save_goal(self, goal: Goal) -> None:
        pass

class JsonGoalRepository(GoalRepository):
    """
    A simple memory-backed mock for now, which can easily be upgraded 
    to write to a JSON file on disk. Proves the storage-agnostic interface.
    """
    def __init__(self):
        # In a real implementation this would load from/save to a JSON file.
        # Format: { project_display_name: [Goal, ...] }
        self._store = {}

    def get_recent_goals(self, project: ProjectIdentity) -> List[Goal]:
        return self._store.get(project.display_name, [])

    def save_goal(self, goal: Goal) -> None:
        # In a real implementation, we'd need to associate it with a project
        # or have the Goal model store the project_id.
        # For the stub, we just accept it and do nothing or store globally.
        pass
        
    def save_project_goal(self, project: ProjectIdentity, goal: Goal) -> None:
        if project.display_name not in self._store:
            self._store[project.display_name] = []
        # Update if exists, else append
        existing = next((g for g in self._store[project.display_name] if g.goal_id == goal.goal_id), None)
        if existing:
            self._store[project.display_name].remove(existing)
        self._store[project.display_name].append(goal)
