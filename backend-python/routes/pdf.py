from fastapi import APIRouter, UploadFile, File, Form
# Corregido para que busque en la carpeta hermana
from services.pdf_service import process_pdf_file

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), chat_id: str = Form(...)):
    """Punto de entrada para subir y procesar el PDF."""
    resultado = process_pdf_file(file, chat_id)

    return resultado
