from typing import Dict, Any
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
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

def extract_rcd_info(rcd_text: str) -> Dict[str, Any]:
    prompt = f"""
    You are an expert skills extractor. Analyze the provided Role Clarity Document and return exactly two lists:

        1. TECHNICAL SKILLS: All hard skills, tools, and technologies required for this role. Separate the combined terms.
        2. SOFT SKILLS: All interpersonal and business skills required for this role

        Output format (strictly follow this JSON structure):
        {{
            "technical_skills": ["list", "of", "technical", "skills"],
            "soft_skills": ["list", "of", "soft", "skills"]
        }}

        Extraction Rules:
        1. For TECHNICAL SKILLS:
        - Include all programming languages, frameworks, libraries, and tools
        - Expand abbreviations (e.g., "RAG" → "Retrieval-Augmented Generation")
        - Include specific techniques mentioned (e.g., "Entity Recognition")
        - Include development practices (e.g., "code reviews")
        - Include any mentioned platforms or cloud services

        2. For SOFT SKILLS:
        - Include communication, collaboration, and leadership requirements
        - Include any mentioned interpersonal skills
        - Include organizational/teamwork skills
        - Exclude technical capabilities

        3. For both lists:
        - Remove duplicates but keep similar skills with different specificity
        - Standardize terms to common industry names
        - Include only skills explicitly mentioned or strongly implied
        - Maintain original capitalization for proper nouns
        - Sort alphabetically

        Focus particularly on extracting:
        - techniques/tools
        - Programming languages and frameworks
        - Development methodologies
        - Communication and collaboration requirements
        - Leadership and mentoring needs

    Document Text:
    {rcd_text}
    """

    extracted_data = {
        "technical_skills": [],
        "soft_skills": []
    }

    try:

        response = model.generate_content(prompt)
        raw_response = response.text.strip()
        clean_response = re.sub(r"^```.*\n|\n```$", "", raw_response).strip()

        if not clean_response:
            raise HTTPException(status_code=400, detail="Empty response from Gemini API.")
        
        try:
            extracted_data = json.loads(clean_response)
            return extracted_data
        except json.JSONDecodeError as json_err:
            raise HTTPException(status_code=400, detail=f"JSON Decode Error: {str(json_err)}. Response may not be valid JSON.")
        
    except json.JSONDecodeError as json_err:
        raise HTTPException(status_code=400, detail=f"JSON Decode Error: {str(json_err)}. Response may not be valid JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
