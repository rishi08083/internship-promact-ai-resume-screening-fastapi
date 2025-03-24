from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/screen_candidate")
async def screen_candidate_endpoint():
    try:
        return {'match_score' : 90, 'details' : 'insights'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")