from desktop.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.web_models import BrowserContext, WebCollection, WebResourceType, WebResource, ExtractionEvidence

class SysWebExtractTextAdapter:
    def execute(self, context: BrowserContext, selector: str = None) -> ExecutionResult:
        # Pipeline: Fetch HTML -> Boilerplate Removal -> Markdown Conversion -> Content Scoring -> Packaging
        
        html = self._fetch_html(context)
        clean_html = self._remove_boilerplate(html)
        markdown = self._convert_to_markdown(clean_html)
        score = self._score_content(markdown)
        
        evidence = ExtractionEvidence(
            url=context.page_state.url if context.page_state else "",
            timestamp=0.0, # Stub
            bytes_count=len(markdown)
        )
        
        collection = WebCollection(
            resource_type=WebResourceType.PAGE.value,
            results=[WebResource(url=evidence.url, title="Extracted Text", metadata={"markdown": markdown}, evidence=evidence)],
            count=1,
            confidence=score,
            completeness=1.0,
            is_partial=False
        )
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"collection": collection})
        
    def _fetch_html(self, context: BrowserContext) -> str:
        # Architecture Note: Crawl4AI handles the fetching and boilerplate removal securely.
        return "<html>Stub</html>"
        
    def _remove_boilerplate(self, html: str) -> str:
        return html
        
    def _convert_to_markdown(self, html: str) -> str:
        return "# Stub Markdown"
        
    def _score_content(self, markdown: str) -> float:
        return 0.95
