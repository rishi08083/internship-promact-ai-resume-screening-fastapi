from typing import List
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()

GEMINI_API_KEY = os.getenv('API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# def extract_skills(rcd_text: str) -> List[str]: 
#     prompt = f"""
#     You are an expert AI job description parser. Extract the **skills** mentioned in the following text and return them as a Python list of strings.

#     Format the response as:
#     ["skill 1", "skill 2", "skill 3", ...]

#     Do not include any extra text, explanations, or formatting.

#     RCD text:
#     {rcd_text}
#     """

#     try:
#         response = model.generate_content(prompt)
#         raw_response = response.text.strip()

#         # Remove markdown-style list formatting if any
#         clean_response = re.sub(r"^```.*\n|\n```$", "", raw_response).strip()

#         if not clean_response:
#             raise ValueError("Empty response for JD Skills extraction from Gemini API.")
        
#         # print("Not formatted : " , clean_response)

#         # # Convert the response into a Python list
#         # extracted_skills = eval(clean_response)

#         # print("Converted : ", extracted_skills)
#         # print("Type : ", type(extracted_skills))

#         # if not isinstance(extracted_skills, list) or not all(isinstance(skill, str) for skill in extracted_skills):
#         #     raise ValueError("Invalid format received from Gemini API.")

#     except (SyntaxError, ValueError) as e:
#         print(f"Parsing error: {str(e)}. Gemini may have returned an unexpected format.")
#     except Exception as e:
#         print(f"Gemini API error: {str(e)}")

#     return clean_response

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
            raise ValueError("Empty response from Gemini API.")

        skill_list = [skill.strip() for skill in clean_response.split(",") if skill.strip()]

        extracted_skills.extend(skill_list)

    except Exception as e:
        print(f"Gemini API error: {str(e)}")

    return extracted_skills

if __name__ == "__main__":
    sample_rcd_text = """
    Deep understanding of AI/ML concepts, algorithms, and techniques, extensive experience in developing and implementing AI/ML models for various use cases, 
    proficiency in programming languages commonly used in AI/ML, such as Python, hands-on experience with popular AI/ML frameworks and libraries 
    (e.g., TensorFlow, PyTorch, Keras, scikit-learn), experience with data preprocessing, feature engineering, and model evaluation techniques, 
    familiarity with Natural Language Processing (NLP) techniques and libraries (e.g., NLTK, spaCy, Transformers), comprehensive knowledge of 
    Generative AI techniques and architectures (e.g., Transformer-based models, GANs, VAEs), experience with Large Language Models (LLMs) and 
    their fine-tuning for specific tasks, understanding of Vector Databases and their applications in AI/ML (e.g., Faiss, Chroma, Azure Search, Elastic Search), 
    experience with Retrieval-Augmented Generation (RAG) and its implementation using LLMs and Vector Databases, knowledge of Semantic Search and 
    its implementation using embeddings and similarity measures, understanding of machine learning pipelines and MLOps practices, 
    familiarity with cloud platforms (AWS, Azure, GCP) and their AI/ML offerings, strong problem-solving skills and ability to develop innovative 
    solutions to complex AI/ML challenges, excellent communication and mentoring skills to effectively guide and collaborate with team members, 
    bachelor's or master's degree in Computer Science, Data Science, or a related field, minimum of 3-4 years of experience in AI/ML development.
    """
    
    extracted_skills = extract_skills(sample_rcd_text)
    print(extracted_skills)
