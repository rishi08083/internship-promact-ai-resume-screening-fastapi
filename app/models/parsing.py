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
    - skills (list of strings): List of technical or soft skills mentioned:
        - tools, technologies and libraries used to develop projects 
        (don't give the full statement, only give technologies and libraries)
        - Contributions and impact made
        - Any automation, optimization, or significant improvements introduced     
    - work experience (list of strings): Projects developed by candidate which are mentioned in resume.
        - Responsibilities undertaken while doing the projects
        - Explain the full projects developed mentioned in resume
        - Positions held during projects
        - Contributions made to the project
        - Functionalities developed during the project
    - experience (list of objects): Each object contains:
        - company (string): Name of the company
        - job_title (string): Job title
        - start_date (string): Start date of the job (format: YYYY-MM)
        - end_date (string): End date of the job (format: YYYY-MM or "Present")
    - education (list of objects): Each object contains:
        - College (string): Name of the college
        - Degree (string): Degree title
        - start_date (string): Start date of the degree/college (format: YYYY-MM)
        - end_date (string): End date of the degree/college (format: YYYY-MM or "Present")
    - locations (list of strings): List of locations mentioned (e.g., cities, countries)

    Ensure the output is a valid JSON string.
    If a field is missing, use null for strings or an empty list for arrays.


- For skill matching:
    - Compare resume skills to skills mentioned in the Job Description and Role Competency Document.
    - Return `matched_skills` (list of resume skills that semantically match the JD or RCD).
    - Return `unmatched_skills` (list of resume skills that do not match JD or RCD).

---


    Resume text:
    {resume_txt}
    """.format(resume_txt=resume_txt)
    resume_txt = resume_txt.lower()
    

    parsed_data = {
        "name": None,
        "email": None,
        "phone": None, 
        "skills": [],
        "work experience": [],
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
    # for i in parsed_data['skills']:
    #     i = i.lower()
    # print('--'*50)
    # print('parsed_data:', parsed_data)
    # print('--'*50)

    return parsed_data