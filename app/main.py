from fastapi import FastAPI
from api import resume

app = FastAPI()


app.include_router(resume.router, prefix="/api", tags=["resume"])
# app.include_router(screening.router, prefix="/api", tags=["screening"])


@app.get("/")
def health_check():
    return {"status": "healthy"}