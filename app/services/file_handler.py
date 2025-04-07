from PyPDF2 import PdfReader
import io 
from fastapi import HTTPException



def extract_text_from_pdf(file_content: bytes):
    try:
        pdf = PdfReader(io.BytesIO(file_content))
        ext_txt = ""

        for page in pdf.pages:
            page_txt = page.extract_text()
            if page_txt:
                ext_txt += page_txt + "\n"
        
        if (len(ext_txt) == 0) or (not ext_txt.strip()):
            raise HTTPException(status_code=400, detail="No text extracted from PDF.")

        return ext_txt

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")