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
def extract_skills(jd_text: str) -> List[str]: 
    prompt = f"""
    You are an expert technical skills extractor. Analyze the following job description and extract all skills as it is:
    - Programming languages (expand abbreviations like "JS" → "JavaScript")
    - Frameworks/libraries (expand like "TF" → "TensorFlow")
    - Tools/platforms (expand like "GCP" → "Google Cloud Platform")
    - Technical methodologies
    - Required technical knowledge areas

    Return ONLY a single line of comma-separated values with these rules:
    1. Expand all abbreviations to full names
    2. Group similar technologies (e.g., "AWS/Azure/GCP" → "AWS, Azure, Google Cloud Platform")
    3. Include proficiency levels when specified (e.g., "advanced Python")
    4. Standardize terms (use "React.js" not "ReactJS")
    5. Exclude non-technical skills and generic terms
    6. Remove duplicates but keep variations with different specificity
    7. Maintain original capitalization for proper nouns

    Example Output:
    Python, JavaScript, TensorFlow, Amazon Web Services, Microsoft Azure, Google Cloud Platform, Natural Language Processing, Docker, Kubernetes

    Input Text:
    {jd_text}
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