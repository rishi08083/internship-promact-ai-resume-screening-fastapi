from typing import Dict

def screen_candidate(resume_data: Dict[str, str], jd_data: Dict[str, str]) -> Dict:

    return {
        "match_score": round(match_score, 2),
        "details": details
    }

def _extract_years(experience: str) -> float:
<<<<<<< Updated upstream
    """
    Extract years of experience from a string (e.g., '5 years' -> 5.0).
    """
=======
    
>>>>>>> Stashed changes
    return 0.0