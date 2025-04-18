from typing import List
import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import HTTPException


load_dotenv(override=True)

GEMINI_API_KEY = os.getenv('API_KEY_2')

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
def extract_skills(rcd_text: str) -> List[str]: 
    prompt = f"""
    You are an expert AI job description parser. Extract all **skills** mentioned in the given text.

    Return the skills **as a single line, comma-separated string**.
    
    Example Output:
    Python programming, Experience with TensorFlow, Knowledge of NLP techniques, Cloud platforms (AWS, Azure, GCP)

    Do not include any extra text, explanations, or formatting.

    RCD text:
    {rcd_text}
    """

    extracted_skills = []

    try:
        
        response = model.generate_content(prompt)
        clean_response = response.text.strip()

        if not clean_response:
            raise HTTPException(status_code=400, detail="Empty response from Gemini API.")

        skill_list = [skill.strip() for skill in clean_response.split(",") if skill.strip()]

        extracted_skills.extend(skill_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    return extracted_skills
