from enum import Enum
from typing import List, Any
from dataclasses import dataclass, field

class EmbeddingStatus(Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class EmbeddingJob:
    """
    Rule 290: Embedding generation is asynchronous.
    """
    job_id: str
    document_id: str
    chunks: List[str] = field(default_factory=list)
    status: EmbeddingStatus = EmbeddingStatus.QUEUED
    model_name: str = "default-embedding-model"

class IEmbeddingProvider:
    """
    Interface for future embedding generators (Local, OpenAI, Nomic, etc.).
    """
    async def generate_embeddings(self, texts: List[str]) -> List[Any]:
        pass

class EmbeddingQueue:
    """
    Manages the asynchronous processing of EmbeddingJobs.
    """
    def __init__(self):
        self.jobs: List[EmbeddingJob] = []

    def enqueue(self, job: EmbeddingJob):
        self.jobs.append(job)

    def get_next(self) -> EmbeddingJob:
        pass
