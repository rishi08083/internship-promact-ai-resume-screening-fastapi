from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.download_file import download_from_s3_to_buffer
from services.file_handler import extract_text_from_pdf
from models.parsing_RCD import extract_rcd_info

router = APIRouter()

class ScreenCandidateRequest(BaseModel):
    job_id: int = Field(..., gt = 0)
    jd_data: Dict[str, any] = Field(..., min_length=1)
    rcd_file_key: str
    candidate: Dict[str, any]             # Only one candidate data passed (id, Skills and exp)

class ScreenCandidateResponse(BaseModel):
    status: str
    candidate: Dict[str, any]                   # Candidate data, including skills and experience
    jd_score: float
    rcd_score: float
    combined_score: float
    feedback: str


@router.post("/screen_candidates", response_model=ScreenCandidateResponse)
async def screen_candidates(req: ScreenCandidateRequest):
    """
    Screen candidates by matching parsed resume skills (from Node.js) with JD and RCD.
    :param request: Request body including job_id, jd_skills, rcd_file_key, and candidate info.
    :return: Ranked list of candidates with scores and feedback.
    """
    try:

        job_id = req.job_id
        jd_data = req.jd_data
        rcd_file_key = req.rcd_file_key
        candidate = req.candidate

        if not jd_data:
            raise HTTPException(status_code=400, detail="No JD skills provided.")
        if not rcd_file_key:
            raise HTTPException(status_code=400, detail="No RCD file key provided.")
        
        rcd_content = download_from_s3_to_buffer(rcd_file_key)
        rcd_text = extract_text_from_pdf(rcd_content)
        rcd_text_cleaned = rcd_text.strip()
        if not rcd_text_cleaned :
            raise HTTPException(status_code=400, detail="RCD file is empty.")
        
        rcd_extension = rcd_file_key.split(".")[-1].lower()
        if rcd_extension != "pdf":
            raise HTTPException(status_code=400, detail="RCD must be a PDF file.")
        
        if not candidate:
            raise HTTPException(status_code=404, detail=f"No parsed resumes found for job_id: {job_id}")
        
        jd_skills = jd_data['skills_required']                      # only str
        jd_title = jd_data['title']                                 # only str      
        jd_exp = jd_data['experience_required']                     # only str
        
        rcd_data = extract_rcd_info(rcd_text_cleaned)               # Gemini Inference.

        candidate_skills = candidate_data.get('skills', [])             # List of str (skills)
        candidate_exp = candidate_data.get('experience', {})            # dictionary -> {title : str, exp : str}
        # candidate_id = candidate_data.get('id', [])                     # candidate id : int


        rcd_skills = rcd_data['skills_required']                    # List of strings 
        rcd_knowledge_areas = rcd_data['knowledge_areas']           # List of strings 

        rcd_tot_skills = {
            "rcd_skills" : rcd_skills,                              # Dict[str, List[str]]
            "rcd_knowledge_areas" : rcd_knowledge_areas             # Dict[str, List[str]]
        }

        scores = screen_candidate(candidate_skills, candidate_exp, jd_skills, jd_title, jd_exp, rcd_tot_skills)
        
        feedback = generate_feedback(
            combined_score=scores[combined_score],
            jd_skills=jd_skills,
            resume_skills=candidate_skills,
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
