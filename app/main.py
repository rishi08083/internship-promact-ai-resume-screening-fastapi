from fastapi import FastAPI
# from app import resume, screening

app = FastAPI(title="AI Recruitment Backend", version="1.0.0")

# app.include_router(resume.router, prefix="/api/v1", tags=["resume"])
# app.include_router(screening.router, prefix="/api/v1", tags=["screening"])

@app.get("/")
def health_check():
    return {"status": "healthy"}