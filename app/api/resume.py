from fastapi import APIRouter, File, UploadFile, HTTPException
from services.file_handler import extract_text_from_pdf
from services.doc_handler import extract_text_from_doc
from services.ocr_handler import extract_text_from_image

router = APIRouter()

@router.post("/parse_pdf_resume")
async def parse_pdf_resume(file: UploadFile = File(...)):
    try:
        file_content = await file.read()

        extracted_text = extract_text_from_pdf(file_content)
                
        return {"status": "success", "Text": extracted_text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/parse_doc_resume")
async def parse_doc_resume(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["docx", "doc"]:
            raise ValueError("Unsupported file format. Only .docx and .doc are supported.")
        extracted_text = extract_text_from_doc(file_content, file_extension)

        return {"status": "success", "Text": extracted_text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.post("/parse_image_resume")
async def parse_image_resume(file: UploadFile = File(...)):
    
    try:
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            raise ValueError("Unsupported file format. Only JPG, JPEG, and PNG are supported.")
        
        file_content = await file.read()

        extracted_text = extract_text_from_image(file_content)

        return {"status": "success", "Text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))