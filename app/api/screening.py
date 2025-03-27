from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.download_file import download_from_s3_to_buffer
from services.file_handler import extract_text_from_pdf

router = APIRouter()

class ScreenCandidateRequest(BaseModel):
    job_id: str
    jd_skills: List[str] = Field(..., min_length=1)
    rcd_file_key: str
    candidates: List[Dict[str, any]]  # List of candidate data passed from Node.js

class ScreenCandidateResponse(BaseModel):
    status: str
    candidate: Dict[str, any]  # Candidate data, including skills and experience
    jd_score: float
    rcd_score: float
    combined_score: float
    feedback: str


@router.post("/screen_candidates", response_model=ScreenCandidateResponse)
async def screen_candidates(request: ScreenCandidateRequest):
    """
    Screen candidates by matching parsed resume skills (from Node.js) with JD and RCD.
    :param request: Request body including job_id, jd_skills, rcd_file_key, and candidate info.
    :return: Ranked list of candidates with scores and feedback.
    """
    try:
        jd_skills = request.jd_skills
        rcd_file_key = request.rcd_file_key
        job_id = request.job_id
        candidates = request.candidates  # Candidates passed from Node.js

        if not jd_skills:
            raise HTTPException(status_code=400, detail="No JD skills provided.")
        if not rcd_file_key:
            raise HTTPException(status_code=400, detail="No RCD file key provided.")

        rcd_content = download_from_s3_to_buffer(rcd_file_key)
        if not rcd_content:
            raise HTTPException(status_code=400, detail="RCD file is empty.")
        
        rcd_extension = rcd_file_key.split(".")[-1].lower()
        if rcd_extension != "pdf":
            raise HTTPException(status_code=400, detail="RCD must be a PDF file.")
        
        rcd_text = extract_text_from_pdf(rcd_content)

        if not candidates:
            raise HTTPException(status_code=404, detail=f"No parsed resumes found for job_id: {job_id}")
        
        #################################################################################################
        ## Send RCD text for proper information structuring via Gemini.
        ###################################################################################################

        # Screen candidates
        results = []
        for candidate in candidates:
            # Ensure the candidate has 'skills' and 'experience' attributes
            skills = candidate.get("skills", [])
            experience = candidate.get("experience", [])

            jd_score, rcd_score, combined_score = screen_candidate(candidate, jd_skills, rcd_text)
            
            feedback = generate_feedback(
                combined_score=combined_score,
                jd_skills=jd_skills,
                resume_skills=skills,
                resume_experience=experience,
                rcd_text=rcd_text
            )

            # Include skills and experience directly in the candidate data in the response
            candidate_data = {
                "skills": skills,
                "experience": experience,
            }

            results.append(ScreenCandidateResponse(
                candidate=candidate_data,  # Return only skills and experience
                jd_score=jd_score,
                rcd_score=rcd_score,
                combined_score=combined_score,
                feedback=feedback
            ))

        # Sort by combined score (descending)
        results.sort(key=lambda x: x.combined_score, reverse=True)

        # Return the first candidate as an example (you can modify this as needed)
        return ScreenCandidateResponse(
            status="success", 
            file_key=results[0].file_key,
            candidate=results[0].candidate,
            jd_score=results[0].jd_score,
            rcd_score=results[0].rcd_score,
            combined_score=results[0].combined_score,
            feedback=results[0].feedback
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Screening failed: {str(e)}")
