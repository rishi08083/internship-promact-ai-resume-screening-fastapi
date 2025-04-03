from PIL import Image
import pytesseract
import io
from typing import Optional
import os

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")

def extract_text_from_image(file_content: bytes) -> str:
    
    try:
        image = Image.open(io.BytesIO(file_content))
        
        extracted_text = pytesseract.image_to_string(image, lang="eng")
        
        if not extracted_text.strip():
            raise ValueError("No text extracted from image.")
        
        return extracted_text
    
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")