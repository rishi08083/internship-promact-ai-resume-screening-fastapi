from fastapi import APIRouter, HTTPException
from services.file_handler import extract_text_from_pdf
from services.doc_handler import extract_text_from_doc
from services.ocr_handler import extract_text_from_image
from models.parsing import parse_resume_text
from services.download_file import download_from_s3_to_buffer

router = APIRouter()

@router.post("/parse_pdf_resume")
async def parse_pdf_resume(file_key : str):
    try:
        file_content = download_from_s3_to_buffer(file_key)
        if not file_content:
            raise HTTPException(status_code=400, detail="PDF file is empty.")
        
        file_extension = file_key.split(".")[-1].lower()
        if file_extension != "pdf":
            raise HTTPException(status_code=400, detail="Unsupported file format. Only .pdf is supported.")

        extracted_text = extract_text_from_pdf(file_content)

        parsed_data = parse_resume_text(extracted_text)
        
        return {"status": "success", "data": parsed_data}
                
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/parse_doc_resume")
async def parse_doc_resume(file_key : str):
    try:
        file_content = download_from_s3_to_buffer(file_key)
        if not file_content:
            raise HTTPException(status_code=400, detail="DOC/DOCX file is empty.")

        file_extension = file_key.split(".")[-1].lower()
        if file_extension not in ["docx", "doc"]:
            raise ValueError("Unsupported file format. Only .docx and .doc are supported.")
        
        extracted_text = extract_text_from_doc(file_content, file_extension)
        parsed_data = parse_resume_text(extracted_text)
        
        return {"status": "success", "data": parsed_data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOC/DOCX processing failed: {str(e)}")

@router.post("/parse_image_resume")
async def parse_image_resume(file_key : str):
    try:
        file_content = download_from_s3_to_buffer(file_key)
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded image file is empty.")

        file_extension = file_key.split(".")[-1].lower()
        if file_extension not in ["jpg", "jpeg", "png"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only JPG, JPEG, and PNG are supported.")
        
        extracted_text = extract_text_from_image(file_content)
        parsed_data = parse_resume_text(extracted_text)
        
        if not any([parsed_data.get("name"), parsed_data.get("email"), parsed_data.get("phone")]):
            raise HTTPException(status_code=400, detail="File does not contain information (no name, email, or phone).")

        return {"status": "success", "data": parsed_data}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))