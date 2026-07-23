from desktop.packages.browser_pack.models.semantic import SearchResults
from desktop.models.presentation import PresentationModel, Widget, TextWidget

class SearchResultsRecipe:
    """
    Defines HOW semantic data becomes a PresentationModel.
    """
    def craft(self, data: SearchResults) -> PresentationModel:
        widgets = []
        for result in data.results:
            widgets.append(TextWidget(id=result.url, content=f"**{result.title}**\n{result.snippet}"))
            
        return PresentationModel(
            model_id=f"search_{data.query}",
            widgets=widgets,
            layout_type="list"
        )
