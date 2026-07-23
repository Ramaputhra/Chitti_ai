from desktop.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.web_models import BrowserContext, WebCollection, WebResourceType, WebResource
from desktop.runtimes.download_runtime import DownloadRuntime

class SysWebDownloadAdapter:
    def execute(self, context: BrowserContext, url: str, expected_path: str, timeout_sec: int = 30) -> ExecutionResult:
        # Step 1: Initiate download via context (e.g. headless browser or http fetch)
        # EventBus.publish(DownloadStartedEvent)
        
        # Step 2: Handoff to DownloadRuntime for OS-level verification
        verifier = DownloadRuntime()
        verification_result = verifier.verify_download(expected_path, timeout_sec)
        
        if verification_result.status == ExecutionStatus.SUCCESS:
            size = verification_result.output_data.get("size", 0)
            collection = WebCollection(
                resource_type=WebResourceType.DOWNLOAD.value,
                results=[WebResource(url=url, title=expected_path, metadata={"size": size})],
                count=1
            )
            return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"collection": collection})
        else:
            return verification_result
