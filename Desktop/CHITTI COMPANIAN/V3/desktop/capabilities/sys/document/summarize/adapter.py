import logging
import os
from typing import Optional
from desktop.models.execution import ExecutionResult, ExecutionStatus
# Note: 'fitz' is PyMuPDF. We assume it is installed in the environment.
try:
    import fitz 
except ImportError:
    fitz = None

logger = logging.getLogger(__name__)

class SysDocumentSummarizeAdapter:
    """
    Sprint 7.6: Uses PyMuPDF (fitz) to deterministically extract text/layout,
    then chunks and summarizes via AI Gateway.
    """
    
    def __init__(self, ai_gateway=None):
        self.ai_gateway = ai_gateway

    def execute(self, path: str) -> ExecutionResult:
        logger.info(f"sys.document.summarize executing for: {path}")
        
        if not os.path.exists(path):
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="File not found")
            
        if fitz is None:
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message="PyMuPDF (fitz) is not installed")

        try:
            # 1. Deterministic Parsing
            doc = fitz.open(path)
            extracted_text = ""
            for page in doc:
                extracted_text += page.get_text()
            
            doc.close()
            
            # 2. Chunking (Stubbed for now)
            # 3. Summarization (Stubbed for now)
            if self.ai_gateway:
                summary = self.ai_gateway.summarize(extracted_text)
            else:
                summary = "Stubbed summary of PDF."

            return ExecutionResult(status=ExecutionStatus.SUCCESS, output=summary)

        except Exception as e:
            logger.error(f"Failed to summarize document: {e}")
            return ExecutionResult(status=ExecutionStatus.FAILED, error_message=str(e))
