from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .api import resume, Screening_2

app = FastAPI()


app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(Screening_2.router, prefix="/api", tags=["screening"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "error": {
                "details": str(exc.detail)  
            }
        }
    )

@app.get("/")
def health_check():
    return {"status": "healthy"}


# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# import os
# from dotenv import load_dotenv

# load_dotenv()

# os.environ["LANGCHAIN_PROJECT"] = "Resume-Matching"
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = os.getenv("Langchain_API")  # fix casing



# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are an AI recruitment assistant. Please check the matching skills of candidate resume with job description and role clarity description given by user. Generate matching score and recommendation whether the candidate should be hire or not. Also show the matched and mismatched skills(without explanation only skills with bullets) both with job description and role clarity."),
#         ("user", "Resume: {resume}\n Job_description: {job_description}\n role_clarity: {role_clarity}")
#     ]
# )
# resume= {"skills": 
#          [
#             "Python",
#             "Linux Security",
#             "Network Security",
#             "Firewalls",
#             "Intrusion Detection Systems (IDS)",
#             "Intrusion Prevention Systems (IPS)",
#             "Cryptography",
#             "Public Key Infrastructure (PKI)",
#             "Ethical Hacking",
#             "Penetration Testing",
#             "Vulnerability Assessment",
#             "Security Information and Event Management (SIEM)",
#             "Risk Management",
#             "Identity and Access Management (IAM)",
#             "Endpoint Security",
#             "Cloud Security (AWS, Azure, GCP)",
#             "Threat Hunting",
#             "Incident Response",
#             "Compliance (GDPR, HIPAA)",
#             "Security Auditing",
#             "Security Protocols (SSL/TLS, VPN)",
#             "SIEM Tools (Splunk, LogRhythm)"
#             ],
#         "experience": [
#             {
#                 "job_title": "aiml",
#                 "experience": "9 year"
#             }
#             ]
#         }
# job_description = {"Skills (Must Have)": "Proficiency in C#, ASP.NET Core (3.x or higher). Deep understanding of database concepts with ORM tools like Entity Framework or Dapper. Understanding on Data Analytics, Reporting and Business Intelligence. Expertise in Angular (2.x or higher), including HTML, CSS, JavaScript, and TypeScript. Knowledge on building customizable/widget-based UI components, dashboard and charting/graphing solutions. Knowledge of Git and project management tools (Jira/Redmine/Azure DevOps/Asana). Understanding of CI/CD tools and practices.",
# "Skills (Specialized)": "Strong experience with mapping and geospatial technologies, including indoor mapping, and integration of Google Maps and Open Street Maps. Proficiency in handling latitude, longitude, and altitude data for mapping purposes. Capabilities in implementing map zoom/pan, markers, etc. integration on web platforms. Experience in developing accessible web-based mapping solutions, considering design adjustments for color blindness. Knowledge in configuring and programming map-based features for real-time situational awareness and complex interface event handling. Skills in sourcing and applying geospatial data in web development. Experience in Geo/Mapping tools e.g. ArcGIS/QGIS.",
# "Skills (Good to Have)": "Basic understanding of DevOps (Docker, Kubernetes, Linux scripting). Networking fundamentals. Conceptual knowledge of Microservices. This position is designed for someone passionate about both software development and the specialized field of mapping and geospatial technologies. The ideal candidate will be innovative, capable of thriving in a fast-paced environment, and dedicated to both team and organizational growth "}
# role_clarity = {
#         "skills_required": [
#         "Communication skills",
#         "Understanding of appropriate methods, tools, applications, and processes",
#         "Creative thinking",
#         "Problem-solving",
#         "Knowledge absorption",
#         "Documentation"
#     ],
#     "knowledge_areas": [
#         "AI/ML models",
#         "Generative AI",
#         "RAG",
#         "Chatbots",
#         "Object Detection",
#         "Semantic Searching",
#         "Entity Recognition",
#         "Data preprocessing",
#         "Feature engineering",
#         "Model evaluation",
#         "Organizational standards",
#         "AI/ML development and security",
#         "Model architecture",
#         "Data processing workflows",
#         "Experiment tracking",
#         "Technical implementation",
#         "Analysis"
#     ],
#     "key_tasks": [
#         "Work closely with the AI/ML team to understand project requirements and propose suitable AI/ML solutions",
#         "Design and implement advanced AI/ML models for various use cases such as Generative AI, RAG, Chatbots, Object Detection, Semantic Searching, Entity Recognition, etc.",
#         "Perform data preprocessing, feature engineering, and model evaluation tasks",
#         "Mentor and guide junior/peer AI/ML engineers, fostering their growth and development",
#         "Conduct code reviews and provide feedback to ensure code quality and adherence to best practices",
#         "Validate developed models against requirements and test cases, ensuring high accuracy and performance",
#         "Identify and mitigate risks associated with AI/ML implementations",
#         "Recommend improvements and updates to AI/ML models and processes",
#         "Collaborate with cross-functional teams and stakeholders to effectively communicate AI/ML solutions and insights",
#         "Assist in the development of organizational standards for AI/ML development and security",
#         "Maintain comprehensive documentation, code comments, and knowledge retention for AI/ML projects",
#         "Adhere to organizational standards for AI/ML development and security",
#         "Clear and concise code commenting",
#         "Design documentation including but not limited to model architecture diagrams, data processing workflows, and experiment tracking",
#         "Technical implementation documentation",
#         "Analysis documentation",
#         "Capturing, sharing, and developing the collective knowledge of the organization",
#         "Participation in Scrum ceremonies",
#         "Time and Task tracking in relevant project management tool"
#     ],
# }

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=os.getenv("API_KEY_2"),
#     temperature=0.3
# )

# output_parser = StrOutputParser()
# chain = prompt | llm | output_parser

# response = chain.invoke({
#     "resume": resume,
#     "job_description": job_description,
#     "role_clarity": role_clarity
# })

# print(response)