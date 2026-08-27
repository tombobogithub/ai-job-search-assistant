from pydantic import BaseModel, ConfigDict

class JobCreate(BaseModel):
    company: str
    title: str
    location: str
    status: str = "saved"

class JobResponse(JobCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)