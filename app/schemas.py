from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    saved = "saved"
    applied = "applied"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"
    withdrawn = "withdrawn"

class JobCreate(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=150)
    location: str = Field(min_length=1, max_length=100)
    status: JobStatus = JobStatus.saved
    job_url: Optional[str] = None
    
class JobUpdate(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    status: Optional[JobStatus] = None
    job_url: Optional[str] = None

class JobResponse(JobCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)