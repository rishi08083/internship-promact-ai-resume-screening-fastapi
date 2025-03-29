from fastapi import FastAPI
from api import resume, Screening_2

app = FastAPI()


# app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(Screening_2.router, prefix="/api", tags=["screening"])


@app.get("/")
def health_check():
    return {"status": "healthy"}