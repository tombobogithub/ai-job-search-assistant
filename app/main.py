from fastapi import FastAPI

app = FastAPI(
    title="AI Job Search Assistant",
    description="Backend API for tracking jobs and analyzing job descriptions.",
    version="0.1.0",
)

@app.get("/")
def root():
    return {"message": "AI Job Search Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}