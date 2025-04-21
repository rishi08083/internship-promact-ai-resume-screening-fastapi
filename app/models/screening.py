# from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from fastapi import HTTPException


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
        You are an AI recruitment assistant. Evaluate candidate fit based on experience range and skill matching. Return results in this exact JSON format:

        {{
            "experience_match": boolean,
            "jd_skill_score": "number",
            "rcd_skill_score": "number",
            "final_skill_score": "number",
            "recommendation": "Yes/No",
            "feedback": "string",
            "jd_mismatch": ["list"],
            "rcd_mismatch": ["list"],
            "jd_match": ["list"],
            "rcd_match": ["list"],
            "experience_info": {{
                "Candidate Experience": "string",
                "Required Experience": "string",
                "Experience Range Check": "string"
            }}
        }}

        Evaluation Rules:

        1. Experience Range Check:
        - Required Experience: {jd_experience['experience']} (interpret as range if hyphenated, else minimum)
        - If range (e.g., "3-5 years"):
        - Match if candidate experience falls within or exceeds
        - Example: 4 years for "3-5" → match
        - If single number (e.g., "5+ years"):
            - Match if candidate meets or exceeds
        - Set "experience_match" True/False accordingly
        - Include range interpretation in "experience_info" (Eg : exceeds requirement, meets requirements, falls short - all in small case)

        2. Skill Matching:
        - Compare candidate skills with both JD and RCD skills
        - For each skill list (JD/RCD):
        - Calculate match percentage (number of matches/total skills)
        - Create separate match/mismatch lists
        - Ensure no skill appears in both match and mismatch and also if a skill is in JD match, that should be also there in RCD match if in RCD.
        - Handle synonyms (e.g., "Python" matches "Python 3.8")
        - Expand abbreviations consistently

        3. Scoring:
        - jd_skill_score: % of JD skills matched (0-100)
        - rcd_skill_score: % of RCD skills matched (0-100)
        - final_skill_score: average of above two
        - recommendation: "Yes" if BOTH:
        - experience_match=True
        - final_skill_score>{THRESHOLD}

        4. Data Provided:
        - Job Title: {", ".join(jd_experience['title'])}
        - Candidate Titles: {", ".join(data_experience['titles'])}
        - Required Exp: {jd_experience['experience']}
        - Candidate Exp: {data_experience['experience']} years
        - JD Skills: {jd_skills}
        - Candidate Skills: {", ".join(data_skills)}
        - RCD Skills: {parsed_rcd}

        5. Output Notes:
        - All scores as numbers without % symbol
        - Empty mismatch lists as "none"
        - Feedback should combine experience and skill insights
        - Experience_info should show range interpretation
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

    feedback = generate_dynamic_feedback(
        data_skills=data_skills, 
        data_experience=data_experience, 
        jd_skills=jd_skills, 
        jd_experience=jd_experience, 
        parsed_rcd=rcd_tot_skills, 
        # final_percent=final_skill_match_percent, 
        # jd_skill_score=jd_skill_percent, 
        # rcd_skill_score=rcd_skill_percent
    )
    Response = {
        "feedback" : feedback
    }

    # Response.update({
    #     "JD_Skill_Match" : jd_skill_percent,
    #     "RCD_Skill_Match" : rcd_skill_percent,
    #     "Combined_Skill_Match" :  final_skill_match_percent
    # })

    return Response
