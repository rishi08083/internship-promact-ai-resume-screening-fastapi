from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from fastapi import HTTPException


model_1 = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv(override=True)  

GEMINI_API_KEY = os.getenv('API_KEY_2') 
THRESHOLD=os.getenv('threshold')
JD_WT = float(os.getenv('jd_wt'))
RCD_WT = float(os.getenv('rcd_wt'))

if not GEMINI_API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    'gemini-2.0-flash', 
    generation_config=genai.GenerationConfig(
        temperature=0,      
        top_k=1
    )
)
def compute_bert_similarity(data_skills, jd_skills):
    embeddings = model_1.encode([data_skills, jd_skills], convert_to_tensor=True)  
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity

def compute_rcd_similarity(data_skills, parsed_rcd):
    
    embeddings = model_1.encode([data_skills, parsed_rcd], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity
    

def generate_dynamic_feedback(data_skills, data_experience, jd_skills, jd_experience, parsed_rcd, final_percent, jd_skill_score, rcd_skill_score):

    prompt2 = f"""
        You are an AI recruitment assistant. Your task is to evaluate whether a candidate is a good fit for a job based 
        on their job experience and skill match scores.Return your feedback in JSON format. Don't use next line after 
        each section, rather keep it comma separated.

        ### **Evaluation Criteria**:
        1. **Experience Match**:
        - Compare the **minimum experience required** in the job description with the candidate’s total years of experience.
        - The candidate must have **equal to or more experience** than required.
        - If the candidate's experience **meets or exceeds** the required experience, set `"experience_match": True`, otherwise, set `"experience_match": False`.

        2. **Final Hiring Recommendation**:
        - If **experience do not match**, give feedback mentioning this `
        - If **experience match**, assess the **final skill match score**:
        - Give insights for the candidate based on the experience criteria and skills criteria.

        ### **Candidate & Job Details**:
        - **Required Job Title:** `{", ".join(jd_experience['title'])}`
        - **Candidate’s Previous Job Titles:** {", ".join(data_experience['titles'])}
        - **Required Experience:** `{jd_experience['experience']} years`
        - **Candidate’s Total Experience:** `{data_experience['experience']} years`
        - **Job Description Required Skills:** `{jd_skills}`
        - **Candidate Skills:** `{", ".join(data_skills)}`
        - **Role Clarity Description Required Skills:** `{parsed_rcd}`
        - **Skill Match Scores**:
        - JD Skill Match Score: `{jd_skill_score}%`
        - RCD Skill Match Score: `{rcd_skill_score}%`
        - Final Skill Match Score: `{final_percent}%`

        ---

        ##Give the output in the following form regardless of any match or mismatch : 
         "experience_match": True/False,
         "recommendation": Yes/No (if final score > `{THRESHOLD}` then recommend, else not),
         "feedback": {"Suggestion"},
         "jd_mismatch": "list of skills from JD that are not present in candidate's skills. Show this regardless of experience mismatch(If nothing found output "none"), also make sure that if a skill is present here it should not be present in matched section. ",
         "rcd_mismatch": "list of skills from RCD that are not present in candidate's skills. Show this regardless of experience mismatch (If nothing found output "none"), also make sure that if a skill is present here it should not be present in matched section.",
         "jd_match": "If JD Skill Match Score <= 0 output "none", else give a list of skills from JD that Match with candidate's skills. Show this regardless of experience mismatch (If nothing found output "none"), also make sure that if a skill is present here it should not be present in mismatched section. ",
         "rcd_match": "If RCD Skill Match Score <= 0 output "none", else give a list of skills from RCD that Match with candidate's skills. Show this regardless of experience mismatch (If nothing found output "none"), also make sure that if a skill is present here it should not be present in mismatched section. ",
         "experience_info": {"Candidate Experience : Candidate's experience mentioned in years", "Required Experience : required expierence mentioned in years"}"

    """

    response = model.generate_content(prompt2)
    
    feedback_text = response.text.strip()

    if feedback_text.startswith("```json"):
        feedback_text = feedback_text[len("```json"):].strip() 
    if feedback_text.endswith("```"):
        feedback_text = feedback_text[:-3].strip()

    try:
        return feedback_text
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI-generated feedback. Raw response: {feedback_text}")

def screen_candidate_and_generate_feedback(data_skills, data_experience, jd_skills, jd_experience, rcd_tot_skills):
    jd_similarity_score = compute_bert_similarity(data_skills, jd_skills)
    jd_skill_score = jd_similarity_score

    rcd_similarity_score_1 = compute_rcd_similarity(data_skills, rcd_tot_skills['rcd_skills'])
    rcd_similarity_score_2 = compute_rcd_similarity(data_skills, rcd_tot_skills['rcd_knowledge_areas'])

    rcd_skill_score = (rcd_similarity_score_1 + rcd_similarity_score_2) / 2
    rcd_skill_percent = max(0, rcd_skill_score) * 100
    jd_skill_percent = max(0, jd_skill_score) * 100


    final_skill_match_percent = (jd_skill_percent * (JD_WT)) + (rcd_skill_percent * (RCD_WT))

    feedback = generate_dynamic_feedback(
        data_skills=data_skills, 
        data_experience=data_experience, 
        jd_skills=jd_skills, 
        jd_experience=jd_experience, 
        parsed_rcd=rcd_tot_skills, 
        final_percent=final_skill_match_percent, 
        jd_skill_score=jd_skill_percent, 
        rcd_skill_score=rcd_skill_percent
    )
    Response = {
        "feedback" : feedback
    }

    Response.update({
        "JD_Skill_Match" : jd_skill_percent,
        "RCD_Skill_Match" : rcd_skill_percent,
        "Combined_Skill_Match" :  final_skill_match_percent
    })

    return Response
