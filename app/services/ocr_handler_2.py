from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import io
import tempfile
import spacy
from pyresparser import ResumeParser

# Load the official spaCy model
nlp = spacy.load("en_core_web_sm")

# Monkey-patch the pyresparser to use it
ResumeParser.nlp = nlp


app = FastAPI()

@app.post("/resume-parse_2/")
async def parse_resume_from_image(file: UploadFile = File(...)):
    try:
        # Step 1: Extract image bytes and convert to text
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)

        # Step 2: Save extracted text as temporary .txt file (PyResparser requires a file)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
            temp_file.write(text)
            temp_file_path = temp_file.name

        # Step 3: Use PyResparser to parse the text-based resume
        parsed_data = ResumeParser(temp_file_path).get_extracted_data()

        return JSONResponse(content=parsed_data)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
