from sentence_transformers import SentenceTransformer, util
import spacy
from typing import Dict

# Load pre-trained models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

def screen_candidate(resume_data: Dict[str, str], jd_data: Dict[str, str]) -> Dict:
    """
    Screen a candidate by comparing resume data to job description data.
    Returns a match score (0-100) and detailed insights.
    """
    # Extract key fields (fallback to empty string if missing)
    resume_skills = resume_data.get("skills", "").split(", ")
    resume_experience = resume_data.get("experience", "")
    jd_skills = jd_data.get("required_skills", "").split(", ")
    jd_experience = jd_data.get("experience", "")

    # Calculate skill match using vector embeddings
    resume_skill_text = " ".join(resume_skills)
    jd_skill_text = " ".join(jd_skills)
    resume_embedding = model.encode(resume_skill_text, convert_to_tensor=True)
    jd_embedding = model.encode(jd_skill_text, convert_to_tensor=True)
    skill_similarity = util.cos_sim(resume_embedding, jd_embedding).item()  # 0 to 1

    # Calculate experience match (simple heuristic for now)
    resume_years = _extract_years(resume_experience)
    jd_years = _extract_years(jd_experience)
    experience_match = min(resume_years / jd_years if jd_years > 0 else 1.0, 1.0)  # Cap at 1.0

    # Weighted scoring (adjust weights as needed)
    skill_weight = 0.6
    exp_weight = 0.4
    match_score = (skill_similarity * skill_weight + experience_match * exp_weight) * 100  # Scale to 0-100

    # Generate insights
    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]
    details = {
        "skill_match": skill_similarity * 100,  # Percentage
        "experience_match": experience_match * 100,  # Percentage
        "missing_skills": missing_skills if missing_skills else "None"
    }

    return {
        "match_score": round(match_score, 2),
        "details": details
    }

def _extract_years(experience: str) -> float:
    """
    Extract years of experience from a string (e.g., '5 years' -> 5.0).
    """
    try:
        # Simple parsing for demo; enhance with regex for production
        for part in experience.split():
            if part.isdigit() or part.replace(".", "").isdigit():
                return float(part)
        return 0.0
    except Exception:
        return 0.0