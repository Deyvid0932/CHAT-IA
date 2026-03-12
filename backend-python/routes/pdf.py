from http.client import HTTPException

from fastapi import APIRouter, UploadFile, File, Form

from config import DB_PATH
from services.database import delete_pdf_db
# Fixed to search in sister folder
from services.pdf_service import process_pdf_file

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), chat_id: str = Form(...)):
    """Entry point to upload and process PDF."""
    # Pass the full UploadFile object to the processing function
    result = process_pdf_file(file, chat_id)
    return result

@router.delete("/delete-pdf/{chat_id}/{file_name}")
async def delete_pdf(chat_id: str, file_name: str):
    success = delete_pdf_db(chat_id, file_name)
    if success:
        return {"message": "Backend: PDF and chunks deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Could not delete file")

