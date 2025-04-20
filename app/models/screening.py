# from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from fastapi import HTTPException
from .trace_screening import generate_dynamic_feedback_2


# model_1 = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv(override=True)  

GEMINI_API_KEY = os.getenv('API_KEY_2') 
THRESHOLD=os.getenv('threshold')
JD_WT = float(os.getenv('jd_wt'))
RCD_WT = float(os.getenv('rcd_wt'))

if not GEMINI_API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0,          
    "top_p": 0.95,            
    "top_k": 1,               
    "max_output_tokens": 8192
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)
# def compute_bert_similarity(data_skills, jd_skills):
#     embeddings = model_1.encode([data_skills, jd_skills], convert_to_tensor=True)  
#     similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
#     return similarity

# def compute_rcd_similarity(data_skills, parsed_rcd):
    
#     embeddings = model_1.encode([data_skills, parsed_rcd], convert_to_tensor=True)
#     similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
#     return similarity
    

def generate_dynamic_feedback(data_skills, data_experience, jd_skills, jd_experience, parsed_rcd,
                            #    final_percent, jd_skill_score, rcd_skill_score
                               ):

    prompt2 = f"""
        You are an AI recruitment assistant. Your task is to evaluate whether a candidate is a good fit for a job based 
        on their job experience and skill match. Calculate the skill match scores yourself and return your feedback in JSON format. 
        Don't use next line after each section, rather keep it comma separated.

        Evaluation Criteria:
        1. Experience Match:
        - Compare the minimum experience required in the job description with the candidate's total years of experience.
        - The candidate must have equal to or more experience than required.
        - If the candidate's experience meets or exceeds the required experience, set `"experience_match": True`, otherwise, set `"experience_match": False`.

        2. **Skill Match Evaluation**:
        - Compare the candidate's skills with both the Job Description (JD) required skills and Role Clarity Description (RCD) required skills.
        - Calculate two separate match percentages:
          * JD Skill Match Score: percentage of JD required skills that match the candidate's skills
          * RCD Skill Match Score: percentage of RCD required skills that match the candidate's skills
        - Calculate a Final Skill Match Score as the average of these two percentages.

        3. **Final Hiring Recommendation**:
        - If **experience does not match**, give feedback mentioning this.
        - If **experience matches**, assess the **final skill match score**:
          * Recommend "Yes" if the Final Skill Match Score is greater than `{THRESHOLD}%`
          * Recommend "No" if the Final Skill Match Score is equal to or less than `{THRESHOLD}%`
        - Give insights for the candidate based on the experience criteria and skills criteria.

        ### **Candidate & Job Details**:
        - **Required Job Title:** `{", ".join(jd_experience['title'])}`
        - **Candidate's Previous Job Titles:** {", ".join(data_experience['titles'])}
        - **Required Experience:** `{jd_experience['experience']} years`
        - **Candidate's Total Experience:** `{data_experience['experience']} years`
        - **Job Description Required Skills:** `{jd_skills}`
        - **Candidate Skills:** `{", ".join(data_skills)}`
        - **Role Clarity Description Required Skills:** `{parsed_rcd}`

        ---

        ##Give the output in the following form regardless of any match or mismatch : 
         "experience_match": True/False,
         "jd_skill_score": "calculated percentage match for JD skills(Strip the percentage Symbol)",
         "rcd_skill_score": "calculated percentage match for RCD skills(Strip the percentage Symbol)",
         "final_skill_score": "average of jd_skill_score and rcd_skill_score(Strip the percentage Symbol)",
         "recommendation": Yes/No (if final_skill_score > `{THRESHOLD}` then recommend, else not),
         "feedback": {"Suggestion"},
         "jd_mismatch": "list of skills from JD that are not present in candidate's skills. Show this regardless of experience mismatch(If nothing found output "none"), also make sure that if a skill is present here it should not be present in matched section. ",
         "rcd_mismatch": "list of skills from RCD that are not present in candidate's skills. Show this regardless of experience mismatch (If nothing found output "none"), also make sure that if a skill is present here it should not be present in matched section.",
         "jd_match": "list of skills from JD that Match with candidate's skills. Show this regardless of experience mismatch (If nothing found output "none"), also make sure that if a skill is present here it should not be present in mismatched section. ",
         "rcd_match": "list of skills from RCD that Match with candidate's skills. Show this regardless of experience mismatch (If nothing found output "none"), also make sure that if a skill is present here it should not be present in mismatched section. ",
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
    # jd_similarity_score = compute_bert_similarity(data_skills, jd_skills)
    # jd_skill_score = jd_similarity_score

    # rcd_similarity_score_1 = compute_rcd_similarity(data_skills, rcd_tot_skills['rcd_skills'])
    # rcd_similarity_score_2 = compute_rcd_similarity(data_skills, rcd_tot_skills['rcd_knowledge_areas'])

    # rcd_skill_score = (rcd_similarity_score_1 + rcd_similarity_score_2) / 2
    # rcd_skill_percent = max(0, rcd_skill_score) * 100
    # jd_skill_percent = max(0, jd_skill_score) * 100


    # final_skill_match_percent = (jd_skill_percent * (JD_WT)) + (rcd_skill_percent * (RCD_WT))

    try:
        feedback = generate_dynamic_feedback_2(
            data_skills=data_skills, 
            data_experience=data_experience, 
            jd_skills=jd_skills, 
            jd_experience=jd_experience, 
            parsed_rcd=rcd_tot_skills
        )
        
        
        return {
            "status": "success",
            "feedback": feedback
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Screening failed: {str(e)}",
            "error": {"details": str(e)}
        }

