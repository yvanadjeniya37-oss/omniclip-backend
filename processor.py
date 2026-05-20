import uuid
import time
import threading
from typing import Dict, Optional
from models import ProcessingJob, JobStatus, VideoFormat

FORMATS = [
    {"name": "YouTube 16:9", "platform": "YouTube", "width": 1920, "height": 1080},
    {"name": "YouTube Short", "platform": "YouTube Shorts", "width": 1080, "height": 1920},
    {"name": "Instagram Post", "platform": "Instagram", "width": 1080, "height": 1080},
    {"name": "Instagram Reel", "platform": "Instagram", "width": 1080, "height": 1920},
    {"name": "Instagram Story", "platform": "Instagram Story", "width": 1080, "height": 1920},
    {"name": "TikTok", "platform": "TikTok", "width": 1080, "height": 1920},
    {"name": "Twitter/X Post", "platform": "Twitter/X", "width": 1280, "height": 720},
    {"name": "Facebook Post", "platform": "Facebook", "width": 1280, "height": 720},
    {"name": "Facebook Story", "platform": "Facebook Story", "width": 1080, "height": 1920},
    {"name": "LinkedIn", "platform": "LinkedIn", "width": 1280, "height": 720},
    {"name": "Snapchat", "platform": "Snapchat", "width": 1080, "height": 1920},
    {"name": "Pinterest", "platform": "Pinterest", "width": 1000, "height": 1500},
]

class VideoProcessor:
    def __init__(self):
        self.jobs: Dict[str, ProcessingJob] = {}

    def create_job(self, contents: bytes, filename: str) -> str:
        job = ProcessingJob.create(filename)
        self.jobs[job.job_id] = job
        thread = threading.Thread(
            target=self._process,
            args=(job.job_id, contents)
        )
        thread.daemon = True
        thread.start()
        return job.job_id

    def _process(self, job_id: str, contents: bytes):
        job = self.jobs[job_id]
        job.status = JobStatus.processing
        total = len(FORMATS)

        for i, fmt in enumerate(FORMATS):
            time.sleep(1.5)
            video_format = VideoFormat(
                name=fmt["name"],
                platform=fmt["platform"],
                width=fmt["width"],
                height=fmt["height"],
                file_url=f"/download/{job_id}/{fmt['platform'].replace('/', '_')}"
            )
            job.formats.append(video_format)
            job.progress = int(((i + 1) / total) * 100)

        job.status = JobStatus.completed
        job.progress = 100

    def get_job(self, job_id: str) -> Optional[dict]:
        job = self.jobs.get(job_id)
        if not job:
            return None
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "formats": [f.dict() for f in job.formats],
            "error": job.error
        }

    def get_results(self, job_id: str) -> Optional[dict]:
        job = self.jobs.get(job_id)
        if not job or job.status != JobStatus.completed:
            return None
        return {
            "job_id": job.job_id,
            "formats": [f.dict() for f in job.formats]
        } 
