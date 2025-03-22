from docx import Document
import io
import win32com.client 
import os

def extract_text_from_doc(file_content : bytes, file_extension: str) :

    file_extension = file_extension.lower()

    if file_extension == "docx":
        try:
            doc = Document(io.BytesIO(file_content))
            txt = [] 
            
            for para in doc.paragraphs:
                if para.text.strip():  
                    txt.append(para.text)
            
            ext_txt= "\n".join(txt) 
            
            if not ext_txt.strip(): 
                raise ValueError("No text extracted from DOCX.")
            
            return ext_txt
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    elif file_extension == "doc":
        try:
            
            with open('temp.doc', 'wb') as file:
                file.write(file_content)

            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False 
            doc = word.Documents.Open(os.path.abspath('temp.doc'))

            ext_txt = doc.Content.Text.strip()
            doc.Close()
            word.Quit()

            os.remove('temp.doc')

            return ext_txt

        except Exception as e:
            raise Exception(f"DOC extraction failed: {str(e)}") 

        finally:
            try:
                if 'doc' in locals():
                    doc.Close()
                if 'word' in locals():
                    word.Quit()
                if os.path.exists('temp.doc'):
                    os.remove('temp.doc')
            except:
                pass

    else:
        raise ValueError(f"Unsupported file extension: {file_extension}. Only 'docx' and 'doc' are supported.")