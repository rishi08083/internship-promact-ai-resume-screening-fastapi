parsed_data = {'status': 'success',
 'data': {'name': 'VINAY DANIDHARIYA',
  'email': 'vinaydanidhariya@gmail.com',
  'skills': ['C/C++',
   'fEATURE ENGINEERING',
   'NLP',
   'Java',
   'Python',
   'SQL',
   'LLM',
   'NodeJS',
   'ExpressJS',
   'AI/ML',
   'Handlebar',
   'MySQL',
   'PostgreSQL',
   'MongoDB',
   'FastAPI',
   'AWS',
   'EC2',
   'S3',
   'algorithms',
   'Lambda',
   'PyTorch',
   'TensorFlow',
   'Full-Stack Development',
   'VS Code',
   'Linux',
   'Git',
   'Postman',
   'Transformer-based models',
   'Problem Solving',
   'Analytical Thinking',
   'Data Structures',
   'Algorithms'],
  'experience': [{'year': '1 year'}],
  'education': ['Marwadi University (NAAC A+)', 'Saurashtra University'],
  'locations': ['Rajkot', 'Gujarat', 'India']}}

parsed_jd = {'title': 'Software Engineer - II (AI/ML)',
 'description': "Promact is looking for an experienced and passionate Software Engineer - II (AI & ML) to play a key role in driving our Artificial Intelligence and Machine Learning initiatives. The candidate will collaborate closely with the AI/ML team to design, develop, implement, and maintain advanced AI/ML models for various projects, ensuring high-quality deliverables and adherence to best practices. Roles and Responsibilities: Work closely with the AI/ML team to understand project requirements and propose suitable AI/ML solutions, design and implement advanced AI/ML models for various use cases such as Generative AI, RAG, Chatbots, Object Detection, Semantic Searching, and Entity Recognition, perform data preprocessing, feature engineering, and model evaluation tasks, mentor and guide junior/peer AI/ML engineers, fostering their growth and development, conduct code reviews and provide feedback to ensure code quality and adherence to best practices, validate developed models against requirements and test cases, ensuring high accuracy and performance, identify and mitigate risks associated with AI/ML implementations, recommend improvements and updates to AI/ML models and processes, collaborate with cross-functional teams and stakeholders to effectively communicate AI/ML solutions and insights, assist in the development of organizational standards for AI/ML development and security, maintain comprehensive documentation, code comments, and knowledge retention for AI/ML projects, actively participate in scrum ceremonies and maintain tracking using relevant project management tools, uphold the organization's values, vision, and mission while fostering a collaborative and innovative work environment, actively participate in and contribute to training sessions to enhance AI/ML skills within the organization.",
 'location': 'Pune, Ahmedabad, Vadodara',
 'experience_required': '3 to 5 years',
 'job_type': 'Work from office',
 'openings': '2',
 'company_name': 'Promact Infotech',
 'skills_required': "Skills (Must Have): Deep understanding of AI/ML concepts, algorithms, and techniques, extensive experience in developing and implementing AI/ML models for various use cases, proficiency in programming languages commonly used in AI/ML, such as Python, hands-on experience with popular AI/ML frameworks and libraries (e.g., TensorFlow, PyTorch, Keras, scikit-learn), experience with data preprocessing, feature engineering, and model evaluation techniques, familiarity with Natural Language Processing (NLP) techniques and libraries (e.g., NLTK, spaCy, Transformers), comprehensive knowledge of Generative AI techniques and architectures (e.g., Transformer-based models, GANs, VAEs), experience with Large Language Models (LLMs) and their fine-tuning for specific tasks, understanding of Vector Databases and their applications in AI/ML (e.g., Faiss, Chroma, Azure Search, Elastic Search), experience with Retrieval-Augmented Generation (RAG) and its implementation using LLMs and Vector Databases, knowledge of Semantic Search and its implementation using embeddings and similarity measures, understanding of machine learning pipelines and MLOps practices, familiarity with cloud platforms (AWS, Azure, GCP) and their AI/ML offerings, strong problem-solving skills and ability to develop innovative solutions to complex AI/ML challenges, excellent communication and mentoring skills to effectively guide and collaborate with team members, bachelor's or master's degree in Computer Science, Data Science, or a related field, minimum of 3-4 years of experience in AI/ML development. Skills (Good to Have): Knowledge of computer vision and image processing techniques (OpenCV, Pillow, scikit-image), familiarity with pre-training techniques for LLMs (e.g., Masked Language Modeling, Next Sentence Prediction), knowledge of Chatbot development frameworks and platforms (e.g., Rasa, Dialogflow), familiarity with Entity Recognition and Extraction techniques (e.g., Named Entity Recognition, Relation Extraction), familiarity with experiment tracking and model versioning tools (MLflow, Weights & Biases), understanding of data privacy and security best practices in AI/ML development.",
 'contact_info': '+91 - 8700393720',
 'salary_range': '500000 - 700000',
 'application_deadline': '2025-03-27'}

jd_skills = parsed_jd["skills_required"]
jd_experience = parsed_jd["experience_required"]
resume_skills = parsed_data["data"]["skills"]
resume_experience = parsed_data["data"]["experience"]

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")
def compute_bert_similarity(resume_skills, jd_skills):
    embeddings = model.encode([resume_skills, jd_skills], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity
similarity_score = compute_bert_similarity(resume_skills, jd_skills)
skill_score = similarity_score * 100
print(f"Similarity Score: {skill_score:.2f}")

import google.generativeai as genai
import os


API_KEY = "GEMINI_API_KEY"  # Replace with your actual Gemini API key (for testing)

# Configure the Gemini AI model
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_dynamic_feedback(resume_skills, jd_skills, skill_score):
    """
    Generates recruiter-friendly feedback based on the candidate's skills, jd_skills, and matching score.
    """
    prompt = f"""
    You are an AI recruitment assistant. You were given skills from candidate resume and skills required from jb description. I will also pass matched score. On the basis of score, you need to say that canditate should be hired or not. Also, show the matched skills only. I will also pass experience required from job description and canditates experience, If skill_score>50, then check the experience, and give your insights.

    Here are the details:

    - **Resume Skills:** {", ".join(resume_skills)}
    - **Job Description Skills:** {jd_skills}
    - **Skill Match Score:** {skill_score}%
    - **Candidate Experience:** {resume_experience}
    - **Required Experience (JD):** {jd_experience}

  """

    response = model.generate_content(prompt)
    return response.text
resume_skills = parsed_data["data"]["skills"]
predefined_skills = jd_skills
skill_score = skill_score
resume_experience = resume_experience
jd_experience = jd_experience
feedback = generate_dynamic_feedback(resume_skills, jd_skills, skill_score)
print("Feedback:", feedback)

