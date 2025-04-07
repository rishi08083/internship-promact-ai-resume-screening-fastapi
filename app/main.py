from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .api import resume, Screening_2

app = FastAPI()


app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(Screening_2.router, prefix="/api", tags=["screening"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "error": {
                "details": str(exc.detail)  
            }
        }
    )

@app.get("/")
def health_check():
    return {"status": "healthy"}