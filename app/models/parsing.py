from typing import Dict, Optional, List
import os
from dotenv import load_dotenv
import json
import re
import google.generativeai as genai
from fastapi import HTTPException


load_dotenv(override=True)

GEMINI_API_KEY = os.getenv('API_KEY')

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

def parse_resume_text(resume_txt : str):
    prompt = """
    You are an expert resume parser. Parse the following resume text and return the result as a valid JSON string:
    - name (string): The candidate's full name
    - email (string): The candidate's email address
    - phone (string): The candidate's phone number (e.g., "+1-123-456-7890", "123-456-7890", or "+91-9876543210")
    - skills (list of strings): Combined list of all skills(from skills section and experience/projects, but avoid including the project names) (if mentioned), such as:
        + tools, technologies and libraries used to develop projects (don't give the full statement, only give technologies and libraries used in it, also avoid including the project name)
        + Any automation, optimization, or significant improvements introduced
    - experience (list of objects): Each object contains:
        + company (string): Name of the company
        + job_title (string): Job title
        + start_date (string): Start date of the job (format: YYYY-MM)
        + end_date (string): End date of the job (format: YYYY-MM or "Present")
    - education (list of objects): Each object contains:
        + College (string): Name of the college
        + Degree (string): Degree title
        + start_date (string): Start date of the degree/college (format: YYYY-MM)
        + end_date (string): End date of the degree/college (format: YYYY-MM or "Present")
    - locations (list of strings): List of geographically valid locations extracted from work experience and education sections (e.g., "New York, USA"). Ensure locations are real and correctly formatted.

    
    Processing Rules:
        1. For skills:
        - Combine all skills from dedicated skills section AND the tools and technologies used in work experience/projects section.
        - Remove duplicates and any inconsistencies.
        - Maintain the coherence.
        - Keep complete skill names including the libraries used. (don't break into sub-components).
        - Include both technical and soft skills make sure it is semantically and logically correct.
        - Expand abbreviations for all abbreviated skills.
        - Standardize terms to common industry names.
        - Maintain original capitalization for proper nouns.
        - Sort alphabetically for consistency.

        2. For experience:
        - Parse both the job metadata and detailed descriptions
        - Extract technologies/tools used from project/role descriptions
        - Include all technologies in the main skills list

        3. For locations:
        - Extract locations only from work experience (e.g., company location) and education (e.g., college/university location) sections.
        - Validate locations to ensure they are real and geographically correct (e.g., exclude "Remote", "N/A", or fictional places).
        - Prioritize explicit mentions in job metadata (e.g., "Google, Mountain View, CA") and education metadata (e.g., "MIT, Cambridge, MA").
        - Use contextual clues from descriptions if metadata is incomplete (e.g., "worked in Seattle" in experience description).
        - Standardize format to "City, Country" where possible (e.g., "London" → "London, United Kingdom").
        - If only a country or state is mentioned, include it as is (e.g., "USA", "California").
        - Remove duplicates and sort alphabetically.
        - Exclude vague or non-geographic terms (e.g., "Global", "Headquarters").

    Ensure the output is a valid JSON string.
    If a field is missing, use null for strings or an empty list for arrays.
    
    Resume text:
    {resume_txt}
    """.format(resume_txt=resume_txt)


    parsed_data = {
        "name": None,
        "email": None,
        "phone": None, 
        "skills": [],
        "experience": [],
        "education": [],
        "locations": []
    }

    try:
        response = model.generate_content(prompt)
        cleaned_response = re.sub(r"```json\s*|\s*```", "", response.text).strip()
        parsed_data = json.loads(cleaned_response)

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}. Falling back to regex parsing.")
        response_text = response.text.lower()
        parsed_data["name"] = re.search(r"(?:name[:\s]*)([A-Za-z\s]+)", response_text)
        parsed_data["name"] = parsed_data["name"].group(1).strip() if parsed_data["name"] else None
        parsed_data["email"] = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resume_txt)
        parsed_data["email"] = parsed_data["email"].group(0) if parsed_data["email"] else None
        parsed_data["phone"] = re.search(r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", resume_txt)
        parsed_data["phone"] = parsed_data["phone"].group(0) if parsed_data["phone"] else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    
    return parsed_data