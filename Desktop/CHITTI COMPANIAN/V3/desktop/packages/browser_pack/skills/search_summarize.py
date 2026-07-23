from desktop.packages.browser_pack.capabilities.search import SearchWebCapability
from desktop.packages.browser_pack.presentation.experiences.search_results import SearchResultsExperience
from desktop.models.environment import EnvironmentContext

class SearchAndSummarizeSkill:
    """
    A tiny composition skill demonstrating orchestration.
    """
    def __init__(self):
        self.search_cap = SearchWebCapability()
        self.experience = SearchResultsExperience()
        
    def execute(self, query: str, context: EnvironmentContext):
        # 1. Search (produces semantic models)
        results = self.search_cap.execute(query, context)
        
        # 2. Present (converts semantic models to Presentation models)
        self.experience.present(results)
        
        # (Future step: Extract Article -> Summarize -> ReaderExperience)
