from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
from models import ProcessingJob
from processor import VideoProcessor

app = FastAPI(title="OmniClip API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = VideoProcessor()

@app.get("/")
def root():
    return {"status": "OmniClip API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
        raise HTTPException(status_code=400, detail="Format vidéo non supporté")
    contents = await file.read()
    job_id = processor.create_job(contents, file.filename)
    return {"job_id": job_id, "status": "processing"}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = processor.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return job

@app.get("/results/{job_id}")
def get_results(job_id: str):
    results = processor.get_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Résultats introuvables")
    return results

@app.get("/download/{job_id}/{filename}")
def download_file(job_id: str, filename: str):
    path = processor.get_output_path(job_id, filename)
    if not path:
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    return FileResponse(path, media_type="video/mp4", filename=filename)

@app.get("/admin/jobs")
def admin_jobs():
    jobs = []
    for job_id, job in processor.jobs.items():
        jobs.append({
            "job_id": job_id,
            "filename": job.filename,
            "status": job.status,
            "progress": job.progress,
            "formats_count": len(job.formats)
        })
    return {"jobs": jobs, "total": len(jobs)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)