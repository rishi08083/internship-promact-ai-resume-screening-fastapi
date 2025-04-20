from fastapi import HTTPException
import io
from unstructured.partition.docx import partition_docx

def extract_text_from_doc(file_content: bytes):
    try:
        file_buffer = io.BytesIO(file_content)
        
        elements = partition_docx(file=file_buffer)
        extracted_text = "\n".join([str(el) for el in elements])
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from DOCX.")
        
        return extracted_text

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX extraction failed: {str(e)}")