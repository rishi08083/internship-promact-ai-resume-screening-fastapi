import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv(override=True)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    top_p=0.95,
    top_k=1,
    max_output_tokens=8192,
    google_api_key=os.getenv('API_KEY_2') 
)

def generate_dynamic_feedback_2(data_skills, data_experience, jd_skills, jd_experience, parsed_rcd):
    prompt_template = ChatPromptTemplate.from_template("""
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
          * Recommend "Yes" if the Final Skill Match Score is greater than `{threshold}%`
          * Recommend "No" if the Final Skill Match Score is equal to or less than `{threshold}%`
        - Give insights for the candidate based on the experience criteria and skills criteria.

        ### **Candidate & Job Details**:
        - **Required Job Title:** `{jd_title}`
        - **Candidate's Previous Job Titles:** {candidate_titles}
        - **Required Experience:** `{jd_exp} years`
        - **Candidate's Total Experience:** `{candidate_exp} years`
        - **Job Description Required Skills:** `{jd_skills}`
        - **Candidate Skills:** `{candidate_skills}`
        - **Role Clarity Description Required Skills:** `{parsed_rcd}`

        ---

        ##Give the output in the following form regardless of any match or mismatch : 
        {{
         "experience_match": True/False,
         "jd_skill_score": "calculated percentage match for JD skills(Strip the percentage Symbol)",
         "rcd_skill_score": "calculated percentage match for RCD skills(Strip the percentage Symbol)",
         "final_skill_score": "average of jd_skill_score and rcd_skill_score(Strip the percentage Symbol)",
         "recommendation": "Yes/No",
         "feedback": {{"Suggestion"}},
         "jd_mismatch": "list of skills from JD that are not present in candidate's skills",
         "rcd_mismatch": "list of skills from RCD that are not present in candidate's skills",
         "jd_match": "list of skills from JD that Match with candidate's skills",
         "rcd_match": "list of skills from RCD that Match with candidate's skills",
         "experience_info": {{
            "Candidate Experience": "{candidate_exp} years",
            "Required Experience": "{jd_exp} years"
         }}
        }}
    """)

    inputs = {
        "jd_title": ", ".join(jd_experience['title']),
        "candidate_titles": ", ".join(data_experience['titles']),
        "jd_exp": jd_experience['experience'],
        "candidate_exp": data_experience['experience'],
        "jd_skills": jd_skills,
        "candidate_skills": ", ".join(data_skills),
        "parsed_rcd": parsed_rcd,
        "threshold": os.getenv('threshold')
    }

    chain = prompt_template | llm | JsonOutputParser()
    
    try:
        response = chain.invoke(inputs)
        
        if isinstance(response, str):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"raw_response": response}
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Screening failed: {str(e)}",
            "error": {"details": str(e)}
        }