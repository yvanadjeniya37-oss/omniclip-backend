import uuid
import time
import threading
import os
import subprocess
from typing import Dict, Optional
from models import ProcessingJob, JobStatus, VideoFormat

FORMATS = [
    {"name": "YouTube 16:9", "platform": "YouTube", "width": 1920, "height": 1080},
    {"name": "YouTube Short", "platform": "YouTubeShorts", "width": 1080, "height": 1920},
    {"name": "Instagram Post", "platform": "Instagram", "width": 1080, "height": 1080},
    {"name": "Instagram Reel", "platform": "InstagramReel", "width": 1080, "height": 1920},
    {"name": "Instagram Story", "platform": "InstagramStory", "width": 1080, "height": 1920},
    {"name": "TikTok", "platform": "TikTok", "width": 1080, "height": 1920},
    {"name": "Twitter/X", "platform": "Twitter", "width": 1280, "height": 720},
    {"name": "Facebook Post", "platform": "Facebook", "width": 1280, "height": 720},
    {"name": "Facebook Story", "platform": "FacebookStory", "width": 1080, "height": 1920},
    {"name": "LinkedIn", "platform": "LinkedIn", "width": 1280, "height": 720},
    {"name": "Snapchat", "platform": "Snapchat", "width": 1080, "height": 1920},
    {"name": "Pinterest", "platform": "Pinterest", "width": 1000, "height": 1500},
]

UPLOAD_DIR = "/tmp/omniclip/uploads"
OUTPUT_DIR = "/tmp/omniclip/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class VideoProcessor:
    def __init__(self):
        self.jobs: Dict[str, ProcessingJob] = {}

    def create_job(self, contents: bytes, filename: str) -> str:
        job = ProcessingJob.create(filename)
        input_path = os.path.join(UPLOAD_DIR, f"{job.job_id}_{filename}")
        with open(input_path, "wb") as f:
            f.write(contents)
        self.jobs[job.job_id] = job
        thread = threading.Thread(
            target=self._process,
            args=(job.job_id, input_path)
        )
        thread.daemon = True
        thread.start()
        return job.job_id

    def _process(self, job_id: str, input_path: str):
        job = self.jobs[job_id]
        job.status = JobStatus.processing
        total = len(FORMATS)
        job_output_dir = os.path.join(OUTPUT_DIR, job_id)
        os.makedirs(job_output_dir, exist_ok=True)

        for i, fmt in enumerate(FORMATS):
            try:
                output_filename = f"{fmt['platform']}.mp4"
                output_path = os.path.join(job_output_dir, output_filename)
                w = fmt["width"]
                h = fmt["height"]
                cmd = [
                    "ffmpeg", "-i", input_path,
                    "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264", "-c:a", "aac",
                    "-y", output_path
                ]
                subprocess.run(cmd, capture_output=True, timeout=120)
                video_format = VideoFormat(
                    name=fmt["name"],
                    platform=fmt["platform"],
                    width=w,
                    height=h,
                    file_url=f"/download/{job_id}/{output_filename}"
                )
                job.formats.append(video_format)
            except Exception as e:
                print(f"Error processing {fmt['platform']}: {e}")
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

    def get_output_path(self, job_id: str, filename: str) -> Optional[str]:
        path = os.path.join(OUTPUT_DIR, job_id, filename)
        if os.path.exists(path):
            return path
        return None