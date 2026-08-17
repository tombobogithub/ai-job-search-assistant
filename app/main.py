from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="AI Job Search Assistant",
    description="Backend API for tracking jobs and analyzing job descriptions.",
    version="0.1.0",
)

class Job(BaseModel):
    company: str
    title: str
    location: str
    status: str = "saved"

jobs ={}
next_id = 1


@app.get("/")
def root():
    return {"message": "AI Job Search Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/jobs")
def create_job(job: Job):
    global next_id

    job_data = job.model_dump()
    job_data["id"] = next_id

    jobs[next_id] = job_data
    next_id += 1

    return job_data

@app.get("/jobs")
def get_jobs():
    return list(jobs.values())

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]

@app.put("/jobs/{job_id}")
def update_job(job_id: int, job: Job):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = job.model_dump()
    job_data["id"] = job_id
    jobs[job_id] = job_data

    return job_data

@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    delete_job = jobs.pop(job_id)

    return {
        "message": "Job deleted",
        "job": delete_job
    }
