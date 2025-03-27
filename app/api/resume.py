from fastapi import APIRouter

router = APIRouter()

@router.post("/parse_resume")
async def parse_resume():
    return {"status": "success", "data": {"name": "placeholder"}}