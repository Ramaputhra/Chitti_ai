from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import WebPageArtifact


class IBrowserProvider(IService):
    """
    Abstracts specific browser automation tools (Playwright, Selenium) for the BrowserCapability.
    """
    def open_url(self, url: str) -> WebPageArtifact:
        ...

    def read_page(self) -> WebPageArtifact:
        ...

    def search(self, query: str) -> WebPageArtifact:
        ...

    def click(self, selector: str) -> WebPageArtifact:
        ...
