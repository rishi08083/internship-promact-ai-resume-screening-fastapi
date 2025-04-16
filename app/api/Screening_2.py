from pydantic import BaseModel, Field
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from app.services.download_file import download_from_s3_to_buffer
from app.services.file_handler import extract_text_from_pdf
from app.services.doc_handler import extract_text_from_doc
from app.models.parsing_RCD import extract_rcd_info
from app.models.screening import screen_candidate_and_generate_feedback
from app.models.parsing_JD_Skiils import extract_skills
from app.services.auth import get_info
import json


router = APIRouter()

class CandidateExperience(BaseModel):
    titles: List[str]                               
    experience: str|int = Field(...)                

class Candidate(BaseModel):
    skill : List[str]                              
    experience : CandidateExperience                


class JD(BaseModel):
    title : str = Field(...)                        
    req_experience : str = Field(...)               
    req_skills : str = Field(...)                   

class ScreenCandidateRequest(BaseModel):
    jd: JD = Field(...)
    rcd_file_key: str = Field(..., min_length=3)
    candidate: Candidate = Field(...)


class ScreenCandidateResponse(BaseModel):
    status: str
    feedback: str|dict
    jd_skill_match : float|int
    rcd_skill_match : float|int
    combined_score : float|int
    

@router.post("/screen_candidates_2", response_model=ScreenCandidateResponse)
async def screen_candidates(req: ScreenCandidateRequest,  payload : dict = Depends(get_info)):
    try:
        jd = req.jd  
        rcd_file_key = req.rcd_file_key  
        candidate = req.candidate  

        if not jd.req_skills:
            raise HTTPException(status_code=400, detail="No skills for JD provided.")
        if not rcd_file_key:
            raise HTTPException(status_code=400, detail="No RCD file key provided.")
        if not candidate.skill:
            raise HTTPException(status_code=404, detail="No candidate skills provided.")
        if not candidate.experience:
            raise HTTPException(status_code=404, detail="No candidate experience provided.")

        candidate_skills = candidate.skill  
        candidate_experience = candidate.experience 

        jd_skills = extract_skills(jd.req_skills)               
        jd_title = jd.title                                     
        jd_experience = jd.req_experience                       
        jd_exp = {
            'title' : jd_title,
            'experience' : jd_experience
        }

        rcd_extension = rcd_file_key.split(".")[-1].lower()
        if rcd_extension != "pdf" and rcd_extension != 'docx':
            raise HTTPException(status_code=400, detail="RCD must be a PDF or a Docx file.")

        rcd_content = download_from_s3_to_buffer(rcd_file_key)
        if rcd_extension == 'pdf':
            rcd_text = extract_text_from_pdf(rcd_content)
        elif rcd_extension == 'docx':
            rcd_text = extract_text_from_doc(rcd_content, rcd_extension)
        rcd_text_cleaned = rcd_text.strip()

        if not rcd_text:
            raise HTTPException(status_code=400, detail="RCD file empty.")

        rcd_data = extract_rcd_info(rcd_text_cleaned)
        rcd_tot_skills = {
            "rcd_skills": rcd_data["skills_required"],  
            "rcd_knowledge_areas": rcd_data["knowledge_areas"],  
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
            jd_skill_match=val['JD_Skill_Match'],
            rcd_skill_match=val['RCD_Skill_Match'],
            combined_score=val['Combined_Skill_Match'],
            feedback=val["feedback"]
        )

        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Screening failed: {str(e)}")
