from desktop.models.execution import ExecutionResult
from desktop.runtimes.web.implementations import SearchRuntime
from desktop.models.web_models import BrowserContext

class SysWebSearchAdapter:
    def execute(self, context: BrowserContext, query: str, limit: int = 10) -> ExecutionResult:
        # Resolves via SearchRuntime and its providers
        runtime = SearchRuntime()
        return runtime.execute_capability(capability_id="sys.web.search", context=context, query=query, limit=limit)
