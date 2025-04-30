import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import time
import random
from fastapi import HTTPException

load_dotenv(override=True)  

# List of API keys
API_KEYS = [
    os.getenv('API_KEY_2'),
    os.getenv('API_KEY_3'),
    os.getenv('API_KEY_4'),
    os.getenv('API_KEY_5'),
    os.getenv('API_KEY_6'),
    os.getenv('API_KEY_7'),
    os.getenv('API_KEY_8'),
    os.getenv('API_KEY_9')
]

# Filter out None values
API_KEYS = [key for key in API_KEYS if key]

if not API_KEYS:
    raise ValueError("No API keys found in environment variables.")

THRESHOLD = os.getenv('threshold')
JD_WT = float(os.getenv('jd_wt'))
RCD_WT = float(os.getenv('rcd_wt'))

# Initialize with a random API key
current_key_index = random.randint(0, len(API_KEYS) - 1)
GEMINI_API_KEY = API_KEYS[current_key_index]

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

def rotate_api_key():
    """Rotate to the next available API key"""
    global current_key_index, GEMINI_API_KEY, model
    
    # Move to the next key
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    GEMINI_API_KEY = API_KEYS[current_key_index]
    
    # Reconfigure genai with the new key
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Recreate the model with the new API key
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )
    
    print(f"Switched to API key {current_key_index + 1} of {len(API_KEYS)}")

def generate_dynamic_feedback(data_skills, data_experience, jd_skills, jd_experience, parsed_rcd):
    max_retries = len(API_KEYS)
    retries = 0
    
    while retries < max_retries:
        try:
            prompt2 = f"""
                You are an AI recruitment assistant. Evaluate candidate fit based on experience range and skill matching. 
                Return results in this exact JSON format:

                {{
                    "experience_match": boolean,
                    "jd_skill_score": "number",
                    "rcd_skill_score": "number",
                    "final_skill_score": "number",
                    "recommendation": "Yes/No",
                    "feedback": "string",
                    "jd_mismatch": ["list"],
                    "rcd_mismatch": ["list"],
                    "jd_match": ["list"],
                    "rcd_match": ["list"],
                    "experience_info": {{
                        "candidate_experience": "string",
                        "required_experience": "string",
                        "experience_range_check": "string"
                    }}
                }}

                Evaluation Rules:

                1. Experience Range Check:
                - Required Experience: {jd_experience['experience']} (interpret as range if hyphenated, else minimum)
                - If range (e.g., "3-5 years"):
                - Match if candidate experience falls within or exceeds
                - Example: 4 years for "3-5" → match
                - If single number (e.g., "5+ years"):
                    - Match if candidate meets or exceeds
                - Set "experience_match" True/False accordingly
                - Include range interpretation in "experience_info" (Eg : 'meets', 'exceeds', 'below' - all in small case)

                2. Skill Matching:
                - Perform two types of matching for 'Candidate Skills' (provided) with: a) 'JD Skills' (provided): Identify matching skills between candidate skills and JD skills. b) 'RCD Skills' (contains technical_skills and soft_skills lists): Match candidate skills with both technical and soft skills, then compute an aggregate RCD score.
                - Matching Logic:
                    - Exact Match: Skills match exactly (case-insensitive, e.g., "Python" matches "python").
                    - Partial Match: Skills with version differences (e.g., "Python" matches "Python 3.8") count as 0.8 of a match.
                    - Synonym Match: Use a synonym map (e.g., "React" matches "React.js", "AWS" matches "Amazon Web Services").
                    - Fuzzy Match: Near-matches (e.g., "NodeJS" vs. "Node.js") with similarity >90% count as 0.9 of a match.
                    - Weighted Matching: If JD/RCD specifies critical skills (e.g., marked as "must-have"), assign double weight to matches/mismatches.
                    - Combined Terms: Handle skills like "AWS Lambda" as distinct from "AWS" but allow partial credit (0.5) if only "AWS" is matched.

                - For JD Skills:
                    -Compare candidate skills against JD skills.
                    -Track matches and mismatches, ensuring no skill appears in both.

                - For RCD Skills:
                    - Match candidate skills against technical_skills and soft_skills separately.
                    - Aggregate score: (0.7 * technical_skill_match_percentage) + (0.3 * soft_skill_match_percentage).
                    - Ensure skills matched in JD are also marked as matched in RCD if present.
            
                - Create separate match/mismatch lists for JD and RCD:
                    - Mismatch lists highlight missing critical skills first.
                    - Use "none" as a single string for empty match/mismatch lists.
                    - If no matching skills found , the match score should be 0 correspondingly.

                - Expand abbreviations consistently across all comparisons (e.g., "JS" → "JavaScript").

                3. Scoring:

                - jd_skill_score:
                    - Calculate as (sum of match weights / sum of total weights) * 100.
                    - Exact match = 1.0, partial match = 0.8, fuzzy match = 0.9, critical skill match = 2.0.


                - rcd_skill_score:
                    - Technical skills: Same weighting as JD.
                    - Soft skills: Exact match = 1.0, no partial/fuzzy matching.
                    - Aggregate: (0.7 * technical_score) + (0.3 * soft_score).

                - final_skill_score: Average of jd_skill_score and rcd_skill_score.
                - recommendation: "Yes" if BOTH:
                - experience_match=True
                - final_skill_score>{THRESHOLD}

                4. Data Provided:
                - Job Title: {", ".join(jd_experience['title'])}
                - Candidate Titles: {", ".join(data_experience['titles'])}
                - Required Exp: {jd_experience['experience']}
                - Candidate Exp: {data_experience['experience']} years
                - JD Skills: {jd_skills}
                - Candidate Skills: {", ".join(data_skills)}
                - RCD Skills: {parsed_rcd}

                5. Output Notes:
                - All scores as numbers without % symbol
                - Empty mismatch lists as "none"
                - Feedback should combine experience and skill insights in third person format(not in first person format)
                - Experience_info should show range interpretation
            """

            response = model.generate_content(prompt2)
            
            feedback_text = response.text.strip()

            if feedback_text.startswith("```json"):
                feedback_text = feedback_text[len("```json"):].strip() 
            if feedback_text.endswith("```"):
                feedback_text = feedback_text[:-3].strip()

            return feedback_text
            
        except Exception as e:
            error_str = str(e)
            print(f"API Key {current_key_index + 1} failed: {error_str}")
            
            # Check if it's a rate limit error
            if "429" in error_str and "quota" in error_str:
                retries += 1
                if retries < max_retries:
                    print(f"Rate limit reached. Rotating to next API key...")
                    rotate_api_key()
                    # Add a small delay before retrying
                    time.sleep(1)
                else:
                    raise HTTPException(
                        status_code=429, 
                        detail="All API keys have reached their rate limits. Please try again later."
                    )
            else:
                # If it's not a rate limit issue, raise the original error
                print(f"Error during Gemini API call: {error_str}")
                raise HTTPException(status_code=500, detail=f"Gemini API error: {error_str}")
    
    # This should not be reached if exceptions are handled properly
    raise HTTPException(status_code=500, detail="Failed to generate feedback after trying all API keys")

def screen_candidate_and_generate_feedback(data_skills, data_experience, jd_skills, jd_experience, rcd_tot_skills):
    feedback = generate_dynamic_feedback(
        data_skills=data_skills, 
        data_experience=data_experience, 
        jd_skills=jd_skills, 
        jd_experience=jd_experience, 
        parsed_rcd=rcd_tot_skills, 
    )
    
    try:
        # Try to parse the feedback as JSON to validate it
        json_feedback = json.loads(feedback)
        
        Response = {
            "feedback": feedback
        }
        return Response
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {feedback}")
        raise HTTPException(status_code=500, detail=f"Failed to parse AI-generated feedback. Error: {str(e)}")