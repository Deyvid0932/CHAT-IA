import os
import shutil
from pypdf import PdfReader
from services.database import guardar_documento, guardar_documento_rag

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def process_pdf_file(file, chat_id):
    # Guardar archivo temporalmente
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text_from_pdf(file_path)
        
        # GUARDAR EN LA BASE DE DATOS (Texto completo y Chunks para RAG)
        guardar_documento(chat_id, file.filename, text)
        guardar_documento_rag(chat_id, file.filename, text)
        
        return {"text": text, "filename": file.filename}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

