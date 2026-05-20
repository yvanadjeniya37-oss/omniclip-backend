from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import time
import uuid

class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class VideoFormat(BaseModel):
    name: str
    platform: str
    width: int
    height: int
    duration: Optional[float] = None
    file_url: Optional[str] = None

class ProcessingJob(BaseModel):
    job_id: str
    filename: str
    status: JobStatus = JobStatus.pending
    progress: int = 0
    created_at: float = 0
    formats: List[VideoFormat] = []
    error: Optional[str] = None

    @classmethod
    def create(cls, filename: str):
        return cls(
            job_id=str(uuid.uuid4()),
            filename=filename,
            status=JobStatus.pending,
            progress=0,
            created_at=time.time(),
            formats=[]
        )

class UploadResponse(BaseModel):
    job_id: str
    status: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    formats: List[VideoFormat] = []
    error: Optional[str] = None 
