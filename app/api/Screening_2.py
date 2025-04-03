from pydantic import BaseModel, Field
from typing import Any, List
from fastapi import APIRouter, HTTPException
from services.download_file import download_from_s3_to_buffer
from services.file_handler import extract_text_from_pdf
from models.parsing_RCD import extract_rcd_info
from models.screening import screen_candidate_and_generate_feedback
from models.parsing_JD_Skiils import extract_skills
import json


router = APIRouter()

class CandidateExperience(BaseModel):
    titles: List[str]                               # titles = ['SDE-1', 'SDE Intern', ...]
    experience: str|int = Field(...)                # Experience = "6" or 6

class Candidate(BaseModel):
    skill : List[str]                               # Skills = ['Java', 'Python', ...]
    experience : CandidateExperience                # CandidateExperience


class JD(BaseModel):
    title : str = Field(...)                        # Title = "AI-ML Engineer"
    req_experience : str = Field(...)               # req_exp = "3-5 years"
    req_skills : str = Field(...)                   # req_skills = "msfdefdmd...."

class ScreenCandidateRequest(BaseModel):
    jd: JD = Field(...)
    rcd_file_key: str = Field(..., min_length=3)
    candidate: Candidate = Field(...)


class ScreenCandidateResponse(BaseModel):
    status: str
    feedback: str|dict
    JD_Skill_Match : float|int
    RCD_Skill_Match : float|int
    Combined_Score : float|int
    

@router.post("/screen_candidates_2", response_model=ScreenCandidateResponse)
async def screen_candidates(req: ScreenCandidateRequest):
    try:
        jd = req.jd  # JD details
        rcd_file_key = req.rcd_file_key  # RCD file key from S3
        candidate = req.candidate  # Candidate details

        if not jd.req_skills:
            raise HTTPException(status_code=400, detail="No JD skills provided.")
        if not rcd_file_key:
            raise HTTPException(status_code=400, detail="No RCD file key provided.")
        if not candidate.skill:
            raise HTTPException(status_code=404, detail="No candidate skills provided.")
        if not candidate.experience:
            raise HTTPException(status_code=404, detail="No candidate experience provided.")

        candidate_skills = candidate.skill  # List of candidate skills
        candidate_experience = candidate.experience  # Candidate experience details (titles, years)

        jd_skills = extract_skills(jd.req_skills)               # Required JD skills in list
        jd_title = jd.title                                     # Job title
        jd_experience = jd.req_experience                       # Required JD experience
        jd_exp = {
            'title' : jd_title,
            'experience' : jd_experience
        }

        rcd_content = download_from_s3_to_buffer(rcd_file_key)
        rcd_text = extract_text_from_pdf(rcd_content)
        rcd_text_cleaned = rcd_text.strip()

        if not rcd_text:
            raise HTTPException(status_code=400, detail="RCD file is empty.")

        rcd_extension = rcd_file_key.split(".")[-1].lower()
        if rcd_extension != "pdf":
            raise HTTPException(status_code=400, detail="RCD must be a PDF file.")

        rcd_data = extract_rcd_info(rcd_text_cleaned)
        rcd_tot_skills = {
            "rcd_skills": rcd_data["skills_required"],  # List[str]
            "rcd_knowledge_areas": rcd_data["knowledge_areas"],  # List[str]
        }

        val = screen_candidate_and_generate_feedback(
            data_skills=candidate_skills,
            data_experience={
                "titles": candidate_experience.titles,
                "experience": candidate_experience.experience
            },
            jd_skills=jd_skills,
            jd_experience=jd_exp,
            rcd_tot_skills=rcd_tot_skills
        )

        feedback_list = json.loads(val['feedback'].replace("\n", ""))

        val['feedback'] = feedback_list

        response = ScreenCandidateResponse(
            status="success",
            JD_Skill_Match=max(0, val['JD_Skill_Match']),
            RCD_Skill_Match=max(0, val['RCD_Skill_Match']),
            Combined_Score=max(0, val['Combined_Skill_Match']),
            feedback=val["feedback"]
        )

        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Screening failed: {str(e)}")

