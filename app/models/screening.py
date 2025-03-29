from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

model_jd = SentenceTransformer("all-MiniLM-L6-v2")
model_rcd = SentenceTransformer("all-MiniLM-L6-v2")
load_dotenv()

GEMINI_API_KEY = os.getenv('API_KEY') 

if not GEMINI_API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def compute_bert_similarity(data_skills, jd_skills):
    embeddings = model_jd.encode([data_skills, jd_skills], convert_to_tensor=True)  
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity

def compute_rcd_similarity(data_skills, parsed_rcd):
    embeddings = model_rcd.encode([data_skills, parsed_rcd], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity

def generate_dynamic_feedback(data_skills, data_experience, jd_skills, jd_experience, parsed_rcd, final_percent, jd_skill_score, rcd_skill_score):

    prompt = f"""
    You are an AI recruitment assistant. You will be given experience required for job along with the job title and 
    canditate's experience on a specific job-title. You need to first check whether the title for the job and any one of the title of 
    candidate's previous experience should match and if not say not to proceed with the candidate and if do set it as TRUE and
    proceed with checking whether experience matches or not. Candidates experience could be more than mentioned 
    job experience. You will be given candidate's detailed resume information, role clarity description(rcd) and job 
    description(jd). I will also pass the JD_Skill_Match, RCD_Skill_Match_Score and final skill matched score between candidate's resume and jd and candidate's 
    resume and rcd . If both job title and experience matches, then Check the final skill score and give your insight and 
    say whether canditate should be hired or not. Return your feedback in JSON format. Use next line after each section.

    Here are the details:
    -**Required experience:** {", ".join(jd_experience)}
    -**Candidate previous job titles:** {", ".join(data_experience['titles'])}
    - **Candidate years of experience: ** {data_experience['experience']}
    - **Candidate skills:** {", ".join(data_skills)}
    - **Job Description Required Skills:** {jd_skills}
    - **Role Clarity Description Required Skills:** {parsed_rcd}
    - **Skill Match Score:** {jd_skill_score, rcd_skill_score, final_percent}%



    Give the output in the following form : 
    
    
    ["title_match : True/False",
    "experience_match : True/False",
    "Give recommendation on the basis of the scores only (if final score > 40 then recommend else not)"]

    """
    
    response = model.generate_content(prompt)
    
    feedback_text = response.text.strip()
    
    if feedback_text.startswith("```json"):
        feedback_text = feedback_text[7:-3].strip() 

    try:

        # Ensure the 'feedback' list is joined into a string
        # if isinstance(feedback_dict.get('feedback', []), list):
        #     feedback_dict['feedback'] = ' '.join(feedback_dict['feedback'])

        # Return the dictionary
        return feedback_text
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI-generated feedback", "raw_feedback": feedback_text}

def screen_candidate_and_generate_feedback(data_skills, data_experience, jd_skills, jd_experience, rcd_tot_skills):
    
    jd_similarity_score = compute_bert_similarity(data_skills, jd_skills)
    jd_skill_score = jd_similarity_score

    # Compute RCD Skills similarity score
    rcd_similarity_score = compute_rcd_similarity(data_skills, str(rcd_tot_skills).lower())
    rcd_skill_score = rcd_similarity_score

    # Final combined score
    final_score = (jd_skill_score * 0.5) + (rcd_skill_score * 0.5)
    final_skill_match_percent = final_score * 100


    feedback = generate_dynamic_feedback(
        data_skills=data_skills, 
        data_experience=data_experience, 
        jd_skills=jd_skills, 
        jd_experience=jd_experience, 
        parsed_rcd=rcd_tot_skills, 
        final_percent=final_skill_match_percent, 
        jd_skill_score=jd_skill_score, 
        rcd_skill_score=rcd_skill_score
    )
    
    Response = {
        "feedback" : feedback
    }

    Response.update({
        "JD_Skill_Match" : jd_skill_score * 100,
        "RCD_Skill_Match" : rcd_skill_score * 100 ,
        "Combined_Skill_Match" : final_skill_match_percent
    })

    return Response


if __name__ == '__main__':

    candidate_exp = {
        'title' : ['AI-ML Engineer', 'Software Developer - 1', 'Software Developer Intern'],
        'experience' : "4 years"
    }

    cd_skills = [
        "Python",
        "R",
        "SQL",
        "TensorFlow",
        "PyTorch",
        "Scikit-Learn",
        "Keras",
        "Numpy",
        "Pandas",
        "Matplotlib",
        "Seaborn",
        "OpenCV",
        "Natural Language Processing (NLP)",
        "Transformers (Hugging Face, BERT, GPT)",
        "Computer Vision",
        "Deep Learning",
        "Machine Learning Model Deployment",
        "MLOps",
        "AWS SageMaker",
        "Google Cloud AI Platform",
        "Microsoft Azure ML",
        "Hyperparameter tuning and optimization",
        "Feature engineering and selection",
        "Data preprocessing and augmentation",
        "Reinforcement Learning",
        "Model Explainability (SHAP, LIME)",
        "Big Data Processing (Hadoop, Spark)",
        "Time Series Forecasting",
        "A/B Testing and Experimentation",
        "Recommendation Systems",
        "Speech Recognition and Synthesis",
        "Edge AI and TinyML",
        "AutoML frameworks",
        "Graph Neural Networks",
        "Bayesian Inference and Probabilistic Models",
        "Federated Learning",
        "Model Compression and Quantization"
    ]



    jd_skills = """
        Skills (Must Have): Deep understanding of AI/ML concepts, algorithms, and techniques, extensive experience in developing and implementing AI/ML models for various use cases, proficiency in programming languages commonly used in AI/ML, such as Python, hands-on experience with popular AI/ML frameworks and libraries (e.g., TensorFlow, PyTorch, Keras, scikit-learn), experience with data preprocessing, feature engineering, and model evaluation techniques, familiarity with Natural Language Processing (NLP) techniques and libraries (e.g., NLTK, spaCy, Transformers), comprehensive knowledge of Generative AI techniques and architectures (e.g., Transformer-based models, GANs, VAEs), experience with Large Language Models (LLMs) and their fine-tuning for specific tasks, understanding of Vector Databases and their applications in AI/ML (e.g., Faiss, Chroma, Azure Search, Elastic Search), experience with Retrieval-Augmented Generation (RAG) and its implementation using LLMs and Vector Databases, knowledge of Semantic Search and its implementation using embeddings and similarity measures, understanding of machine learning pipelines and MLOps practices, familiarity with cloud platforms (AWS, Azure, GCP) and their AI/ML offerings, strong problem-solving skills and ability to develop innovative solutions to complex AI/ML challenges, excellent communication and mentoring skills to effectively guide and collaborate with team members, bachelor's or master's degree in Computer Science, Data Science, or a related field, minimum of 3-4 years of experience in AI/ML development. Skills (Good to Have): Knowledge of computer vision and image processing techniques (OpenCV, Pillow, scikit-image), familiarity with pre-training techniques for LLMs (e.g., Masked Language Modeling, Next Sentence Prediction), knowledge of Chatbot development frameworks and platforms (e.g., Rasa, Dialogflow), familiarity with Entity Recognition and Extraction techniques (e.g., Named Entity Recognition, Relation Extraction), familiarity with experiment tracking and model versioning tools (MLflow, Weights & Biases), understanding of data privacy and security best practices in AI/ML development."""
    
    jd_exp = {
        'title' : "software engineer - ii (ai/ml)",
        'experience' : '3-5 years'
    }

    rcd_tot_skills = {
        "rcd_skills":  [
        "Communication skills",
        "Understanding of appropriate methods, tools, applications, and processes",
        "Creative thinking",
        "Problem-solving",
        "Knowledge absorption",
        "Documentation"
    ],
        "rcd_knowledge_areas":  [
        "AI/ML models",
        "Generative AI",
        "RAG",
        "Chatbots",
        "Object Detection",
        "Semantic Searching",
        "Entity Recognition",
        "Data preprocessing",
        "Feature engineering",
        "Model evaluation",
        "Organizational standards",
        "AI/ML development and security",
        "Model architecture",
        "Data processing workflows",
        "Experiment tracking",
        "Technical implementation",
        "Analysis"
    ]
    }

    res = screen_candidate_and_generate_feedback(cd_skills, candidate_exp, jd_skills, jd_exp, rcd_tot_skills)
    print(res)