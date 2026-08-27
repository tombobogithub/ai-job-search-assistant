from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Job Search Assistant",
    description="Backend API for tracking jobs and analyzing job descriptions.",
    version="0.3.0",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")

def root():
    return {"message": "AI Job Search Assistant API is running"}

@app.get("/health")

def health_check():
    return {"status": "healthy"}

@app.post("/jobs", response_model=schemas.JobResponse)

def create_job(
    job: schemas.JobCreate,
    db: Session = Depends(get_db),

):

    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs", response_model=list[schemas.JobResponse])

def get_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()