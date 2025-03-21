from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import resume

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api", tags=["resume"])
# app.include_router(screening.router, prefix="/api/v1", tags=["screening"])


@app.get("/")
def health_check():
    return {"status": "healthy"}