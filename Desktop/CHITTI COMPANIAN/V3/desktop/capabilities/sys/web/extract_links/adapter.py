from desktop.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.web_models import BrowserContext, WebCollection, WebResourceType

class SysWebExtractLinksAdapter:
    def execute(self, context: BrowserContext, selector: str = None) -> ExecutionResult:
        collection = WebCollection(
            resource_type=WebResourceType.LINK.value,
            results=[],
            count=0
        )
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"collection": collection})
