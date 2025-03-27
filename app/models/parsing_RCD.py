from typing import Dict, List, Any
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

GEMINI_API_KEY = os.getenv('API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def extract_rcd_info(rcd_text: str) -> Dict[str, Any]:
    
    prompt = f'''
        You are an expert job description parser. Extract the following details from the given Role Clarity Document (RCD)
        and return a valid JSON string, formatted correctly.

        Ensure the response is **only** valid JSON with keys and values matching:
        {{
            "role_name": "string",
            "role_summary": "string",
            "responsibilities": ["string", ...],
            "skills_required": ["string", ...],
            "knowledge_areas": ["string", ...],
            "experience": ["string", ...],
            "key_tasks": ["string", ...],
            "training_requirements": ["string", ...]
        }}

        Do **not** include any additional explanation or formatting.

        RCD text:
        {rcd_text}
    '''

    extracted_data = {
        "role_name": None,
        "role_summary": None,
        "responsibilities": [],
        "skills_required": [],
        "knowledge_areas": [],
        "experience": [],
        "key_tasks": [],
        "training_requirements": []
    }
    
    try:
        response = model.generate_content(prompt)
        raw_response = response.text.strip()

        # Remove surrounding triple backticks (if any)
        clean_json = re.sub(r"^```json|```$", "", raw_response).strip()
        
        if not clean_json:  
            raise ValueError("Empty response from Gemini API.")
    
        extracted_data = json.loads(clean_json)  
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error: {str(e)}. Falling back to manual extraction.")
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
    
    return extracted_data

if __name__ == "__main__":
    sample_rcd_text = """
    Role Name:
    Software Engineer – II (AI & ML)

    Role Summary:
    The Software Engineer - II (AI/ML) is responsible for developing, designing, and implementing advanced AI/ML models and solutions for various projects. They work under routine direction, assisting immediate colleagues in achieving organizational and team goals while demonstrating more independence in their role within the AI/ML domain.

    Responsibilities:
    Autonomy:
    Work under routine direction of Reporting Managers

    Determine when to seek guidance from senior members

    Influence:
    Immediate influence towards colleagues to maintain efficient execution of all practices and processes

    Complexity:
    Perform a range of work activities focused on achieving organizational standards and goals

    Contribute to routine issue resolution

    Apply creative thinking and suggest improved approaches to work

    Business Skills:
    Must have sufficient oral and written communication skills for effective engagement with colleagues and internal stakeholders

    Must understand and use appropriate methods, tools, applications, and processes

    Identify and negotiate personal development opportunities

    Must be fully aware of all organizational standards

    Knowledge:
    Must have a clear understanding of fundamentals and primary work area

    Must absorb and apply new information effectively

    Tasks & Activities:
    Development & Verification:
    Work closely with the AI/ML team to understand project requirements and propose suitable AI/ML solutions

    Design and implement advanced AI/ML models for various use cases such as Generative AI, RAG, Chatbots, Object Detection, Semantic Searching, Entity Recognition, etc.

    Perform data preprocessing, feature engineering, and model evaluation tasks

    Mentor and guide junior/peer AI/ML engineers, fostering their growth and development

    Conduct code reviews and provide feedback to ensure code quality and adherence to best practices

    Validate developed models against requirements and test cases, ensuring high accuracy and performance

    Identify and mitigate risks associated with AI/ML implementations

    Recommend improvements and updates to AI/ML models and processes

    Collaborate with cross-functional teams and stakeholders to effectively communicate AI/ML solutions and insights

    Assist in the development of organizational standards for AI/ML development and security

    Maintain comprehensive documentation, code comments, and knowledge retention for AI/ML projects

    Adhere to organizational standards for AI/ML development and security

    Documentation and Knowledge Management:
    Clear and concise code commenting

    Design documentation including but not limited to model architecture diagrams, data processing workflows, and experiment tracking

    Technical implementation documentation

    Analysis documentation

    Capturing, sharing, and developing the collective knowledge of the organization

    Organization Culture Adherence:
    Maintain organization values, vision, and mission

    Active participation in organization activities

    Reporting:
    Participation in Scrum ceremonies

    Time and Task tracking in relevant project management tool

    Training and Learning Orientation:
    Active participation in training provided by the organization, contributing to team learning

    """
    
    extracted_info = extract_rcd_info(sample_rcd_text)
    # print(json.dumps(extracted_info, indent=4))
    print(extracted_info)