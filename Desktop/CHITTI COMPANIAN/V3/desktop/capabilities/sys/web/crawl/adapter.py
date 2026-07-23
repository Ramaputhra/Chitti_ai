from desktop.models.execution import ExecutionResult
from desktop.runtimes.web.implementations import CrawlerRuntime
from desktop.models.web_models import BrowserContext

class SysWebCrawlAdapter:
    def execute(self, context: BrowserContext, url: str, max_depth: int = 2) -> ExecutionResult:
        # Architecture Note: CrawlerRuntime and this adapter should wrap Crawl4AI
        # to handle multi-page crawling, link discovery, and JS rendering.
        runtime = CrawlerRuntime()
        return runtime.execute_capability(capability_id="sys.web.crawl", context=context, url=url, max_depth=max_depth)
