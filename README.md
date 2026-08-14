# AI Job Search Assistant

A full-stack application for tracking job applications and analyzing job descriptions

## Current Status

Day 1:
- FastAPI backend initiated
- Health-check endpoint implemented
- API documentation available through Swagger UI

## Tech Stack

- Python
- FastAPI

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload