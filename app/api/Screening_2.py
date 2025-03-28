from pydantic import BaseModel, Field
from typing import Dict
from fastapi import APIRouter, HTTPException
from services.download_file import download_from_s3_to_buffer
from services.file_handler import extract_text_from_pdf
from models.parsing_RCD import extract_rcd_info
from models.screening import screen_candidate_and_generate_feedback

router = APIRouter()

class ScreenCandidateRequest(BaseModel):
    job_id: int = Field(..., gt=0)
    jd_data: Dict[str, any] = Field(..., min_length=1)
    rcd_file_key: str
    candidate: Dict[str, any]  # Only one candidate data passed (Skills, and experience:{'title', 'experience'})


class ScreenCandidateResponse(BaseModel):
    status: str
    candidate: Dict[str, any]  # Candidate data, including skills and experience
    skills_score: float
    Exp_score: float
    feedback: str


@router.post("/screen_candidates", response_model=ScreenCandidateResponse)
async def screen_candidates(req: ScreenCandidateRequest):
    
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

        if not rcd_text_cleaned:
            raise HTTPException(status_code=400, detail="RCD file is empty.")

        rcd_extension = rcd_file_key.split(".")[-1].lower()
        if rcd_extension != "pdf":
            raise HTTPException(status_code=400, detail="RCD must be a PDF file.")

        if not candidate:
            raise HTTPException(status_code=404, detail=f"No parsed resumes found for job_id: {job_id}")

        jd_skills = jd_data['skills_required']                  # List of skills (str)
        jd_title = jd_data['title']                             # Job title (str)
        jd_exp = jd_data['experience_required']                 # Required experience (str)

        rcd_data = extract_rcd_info(rcd_text_cleaned)
        rcd_skills = rcd_data['skills_required']                # List of strings
        rcd_knowledge_areas = rcd_data['knowledge_areas']       # List of strings

        rcd_tot_skills = {
            "rcd_skills": rcd_skills,                       # Dict[str, List[str]]
            "rcd_knowledge_areas": rcd_knowledge_areas      # Dict[str, List[str]]
        }

        candidate_skills = candidate.get('skills', [])          # List of skills (str)
        candidate_exp = candidate.get('experience', {})         # Dictionary of experience data(title, no. of years)


        val = screen_candidate_and_generate_feedback(
            candidate_skills, candidate_exp, jd_skills, jd_exp, jd_title, rcd_tot_skills)

        # scores = screen_candidate(candidate_skills, candidate_exp, jd_skills, jd_title, jd_exp, rcd_tot_skills)

        # feedback = generate_feedback(
        #     combined_score=scores['combined_score'],
        #     jd_skills=jd_skills,
        #     resume_skills=candidate_skills,
        #     resume_experience=candidate_exp,
        #     rcd_text=rcd_text
        # )

        candidate_data = {
            "skills": candidate_skills,
            "experience": candidate_exp,
        }

        response = ScreenCandidateResponse(
            status="success",
            candidate=candidate_data,
            jd_score=val['jd_score'],
            rcd_score=val['rcd_score'],
            combined_score=val['combined_score'],
            feedback=val['feedback']
        )

        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Screening failed: {str(e)}")
