from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class JobCreate(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=150)
    location: str = Field(min_length=1, max_length=100)
    status: str = "saved"
    
class JobUpdate(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class JobResponse(JobCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)