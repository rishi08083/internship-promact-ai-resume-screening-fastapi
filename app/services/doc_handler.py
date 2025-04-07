from docx import Document
from fastapi import HTTPException
import io

def extract_text_from_doc(file_content: bytes, file_extension: str) -> str:
    
    file_extension = file_extension.lower()

    if file_extension != "docx":
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {file_extension}. Only 'docx' is supported.")

    try:
        doc = Document(io.BytesIO(file_content))
        txt = []

        for para in doc.paragraphs:
            if para.text.strip(): 
                txt.append(para.text)

        ext_txt = "\n".join(txt)

        if not ext_txt.strip():
            raise HTTPException(status_code=400, detail="No text extracted from DOCX.")

        return ext_txt

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX extraction failed: {str(e)}")