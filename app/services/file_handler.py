from PyPDF2 import PdfReader
import io 


def extract_text_from_pdf(file_content: bytes):
    try:
        pdf = PdfReader(io.BytesIO(file_content))
        ext_txt = ""

        for page in pdf.pages:
            page_txt = page.extract_text()
            if page_txt:
                ext_txt += page_txt + "\n"
        
        if (len(ext_txt) == 0) or (not ext_txt.strip()):
            raise ValueError("No text extracted from PDF.")

        return ext_txt

    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")