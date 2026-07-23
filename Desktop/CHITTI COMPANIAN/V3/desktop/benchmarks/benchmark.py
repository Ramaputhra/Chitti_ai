import time
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from dataclasses import dataclass

from desktop.models.goals import Goal
from desktop.models.assessments import GoalAssessment

@dataclass
class BenchmarkMetadata:
    id: str
    name: str
    layer: str
    deterministic: bool
    required_capabilities: List[str]
    description: str

@dataclass
class BenchmarkResult:
    benchmark_id: str
    passed: bool
    latency_ms: float
    events_count: int
    goal_status: str
    error_message: Optional[str] = None
    extracted_path: Optional[str] = None


class CognitiveBenchmark(ABC):
    """
    Every Benchmark is a first-class object testing the Cognitive Spine.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> BenchmarkMetadata:
        pass
        
    @abstractmethod
    def setup(self, event_bus: Any, registry: Any) -> Goal:
        """
        Sets up the environment, mocks, or data and returns the triggering Goal.
        """
        pass
        
    @abstractmethod
    def execute(self) -> Any:
        """
        Must exercise the ENTIRE cognitive spine: Goal -> Context -> Planner -> Translator -> Execution -> Evaluation.
        """
        pass
        
    @abstractmethod
    def assert_success(self, result_data: Any) -> BenchmarkResult:
        """
        Asserts the architectural contracts were maintained and goal satisfied.
        """
        pass
