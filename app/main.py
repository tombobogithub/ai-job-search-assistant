from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Job Search Assistant",
    description="Backend API for tracking jobs and analyzing job descriptions.",
    version="0.5.0",
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
def get_jobs(
    status: str | None = None,
    company: str | None = None,
    sort: str = "newest",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    ):
    query = db.query(models.Job)

    if status:
        query = query.filter(models.Job.status == status)

    if company:
        query = query.filter(
            models.Job.company.ilike(f"%{company}%")
        )

    if sort == "oldest":
        query = query.order_by(models.Job.created_at.asc())
    else:
        query = query.order_by(models.Job.created_at.desc())

    return query.offset(offset).limit(limit).all()


@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    db_job = (
        db.query(models.Job)
        .filter(models.Job.id == job_id)
        .first()
    )

    if db_job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return db_job


@app.patch("/jobs/{job_id}", response_model=schemas.JobResponse)
def patch_job(
    job_id: int,
    job: schemas.JobUpdate,
    db: Session = Depends(get_db),
):
    db_job = (
        db.query(models.Job)
        .filter(models.Job.id == job_id)
        .first()
    )

    if db_job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    update_data = job.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_job, field, value)

    db.commit()
    db.refresh(db_job)

    return db_job


@app.put("/jobs/{job_id}", response_model=schemas.JobResponse)
def update_job(
    job_id: int,
    job: schemas.JobCreate,
    db: Session = Depends(get_db),
):
    db_job = (
        db.query(models.Job)
        .filter(models.Job.id == job_id)
        .first()
    )

    if db_job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    db_job.company = job.company
    db_job.title = job.title
    db_job.location = job.location
    db_job.status = job.status

    db.commit()
    db.refresh(db_job)

    return db_job


@app.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    db_job = (
        db.query(models.Job)
        .filter(models.Job.id == job_id)
        .first()
    )

    if db_job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    db.delete(db_job)
    db.commit()

    return {"message": "Job deleted"}