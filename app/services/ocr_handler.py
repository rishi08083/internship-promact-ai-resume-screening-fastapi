from PIL import Image
import pytesseract
import io
from typing import Optional

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(file_content: bytes) -> str:
    
    try:
        image = Image.open(io.BytesIO(file_content))
        
        extracted_text = pytesseract.image_to_string(image, lang="eng")
        
        if not extracted_text.strip():
            raise ValueError("No text extracted from image.")
        
        return extracted_text
    
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")