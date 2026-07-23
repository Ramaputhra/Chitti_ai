from desktop.packages.browser_pack.presentation.recipes.search import SearchResultsRecipe
from desktop.packages.browser_pack.models.semantic import SearchResults

class SearchResultsExperience:
    """
    Defines WHAT the user sees, integrating with the Presentation Engine.
    """
    def __init__(self):
        self.recipe = SearchResultsRecipe()

    def present(self, results: SearchResults):
        model = self.recipe.craft(results)
        print(f"[SearchResultsExperience] Presenting {len(results.results)} results for '{results.query}' to UI.")
        # In a real flow, this sends the model to the PresentationRuntime's ExperienceInstance
