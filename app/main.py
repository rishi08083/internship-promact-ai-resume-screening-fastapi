from fastapi import FastAPI
from api import resume

# from app import resume, screening

app = FastAPI()

app.include_router(resume.router, prefix="/api", tags=["resume"])
# app.include_router(screening.router, prefix="/api/v1", tags=["screening"])

@app.get("/")
def health_check():
    return {"status": "healthy"}