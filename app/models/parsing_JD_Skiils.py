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
    You are an expert AI job description parser. Go through each line of job description file and extract only the **skills** mentioned in the given text. 
    Skills only include technology, libraries, programming language, tools.
    Return the skills **as a single line, comma-separated string**.
    
    Example Input:
    Skills (Must Have): Proficiency in C#, ASP.NET Core (3.x or higher), deep understanding of database concepts with ORM tools like Entity Framework or Dapper, understanding of Data Analytics, Reporting, and Business Intelligence, expertise in Angular (2.x or higher), including HTML, CSS, JavaScript, and TypeScript, knowledge of building customizable/widget-based UI components, dashboards, and charting/graphing solutions, knowledge of Git and project management tools (Jira/Redmine/Azure DevOps/Asana), understanding of CI/CD tools and practices. Skills (Specialized): Strong experience with mapping and geospatial technologies, including indoor mapping and integration of Google Maps and OpenStreetMap, proficiency in handling latitude, longitude, and altitude data for mapping purposes, capabilities in implementing map zoom/pan, markers, and other interactive features on web platforms, experience in developing accessible web-based mapping solutions with design considerations for color blindness, knowledge in configuring and programming map-based features for real-time situational awareness and complex interface event handling, skills in sourcing and applying geospatial data in web development, experience in Geo/Mapping tools such as ArcGIS/QGIS. Skills (Good to Have): Basic understanding of DevOps (Docker, Kubernetes, Linux scripting), networking fundamentals, conceptual knowledge of Microservices.
    Example Output:
    ['C#', 'ASP.NET Core', 'database concepts', 'ORM tools', 'Entity Framework', 'Dapper', 'Data Analytics', 'Reporting', 'Business Intelligence', 'Angular', 'HTML', 'CSS', 'JavaScript', 'TypeScript', 'UI components', 'charting/graphing solutions', 'Git', 'project management tools', 'Jira', 'Redmine', 'Azure DevOps', 'CI/CD tools', 'mapping and geospatial technologies', 'interactive features', 'accessible web-based mapping solutions', 'configuring and programming map-based features', 'real-time situational awareness', 'complex interface event handling', 'sourcing and applying geospatial data', 'Geo/Mapping tools', 'ArcGIS/QGIS', 'DevOps', 'Docker', 'Kubernetes', 'Linux scripting', 'networking fundamentals', 'Microservices']


    Do not include any extra text, explanations, or formatting.

    JD text:
    {jd_text}
    """
    
    # print('Parser ->',(jd_text).lower())
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
    
    ext_skills = [skill.lower() for skill in extracted_skills]
    # print(ext_skills)
    return ext_skills
