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
    prompt = f'''
        You are an expert job description parser. Extract the following details from the given Role Clarity Document (RCD)
        and return the data in Python dictionary format with the keys and values matching:
        
        {{
            "skills_required": ["string", ...],
            "knowledge_areas": ["string", ...],
        }}

        Do **not** include any additional explanation or formatting.

        RCD text:
        {rcd_text}
    '''

    extracted_data = {
        "skills_required": [],
        "knowledge_areas": []
    }

    try:
        
        generation_config = {
            "temperature": 0,
            "top_p": 1
        }

        response = model.generate_content(prompt)
        raw_response = response.text.strip()
        clean_response = re.sub(r"^```.*\n|\n```$", "", raw_response).strip()

        if not clean_response:
            raise HTTPException(status_code=400, detail="Empty response from Gemini API.")
        
        try:
            extracted_data = json.loads(clean_response)
        except json.JSONDecodeError as json_err:
            raise HTTPException(status_code=400, detail=f"JSON Decode Error: {str(json_err)}. Response may not be valid JSON.")
        
    except json.JSONDecodeError as json_err:
        raise HTTPException(status_code=400, detail=f"JSON Decode Error: {str(json_err)}. Response may not be valid JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    return extracted_data
