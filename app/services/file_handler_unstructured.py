import io
from fastapi import HTTPException
from unstructured.partition.pdf import partition_pdf 

def extract_text_from_pdf(file_content: bytes):
    try:
        file_buffer = io.BytesIO(file_content)
        
        content = partition_pdf(file=file_buffer, strategy="auto")
        
        extracted_text = "\n".join([str(x) for x in content])
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from PDF.")
        return extracted_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")