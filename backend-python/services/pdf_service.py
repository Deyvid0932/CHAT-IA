import os
import shutil
import chromadb
from pypdf import PdfReader
from config import DB_PATH
from services.database import save_document, save_document_rag

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def process_pdf_file(file, chat_id):
    # Save file temporarily
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text_from_pdf(file_path)

        save_document(chat_id, file.filename, text)

        dates_confirmed = save_document_rag(chat_id, file.filename, text)

        if dates_confirmed:
            print("🚀 Intentando conectar con ChromaDB...")
            client = chromadb.PersistentClient(path=DB_PATH)
            col = client.get_or_create_collection(name="document_chunks")

            ids_list = [str(item['id']) for item in dates_confirmed]
            docs_list = [item['content'] for item in dates_confirmed]

            col.add(
                ids=ids_list,
                documents=docs_list,
                metadatas=[{
                    "chat_id": chat_id,
                    "file_name": file.filename,
                    "idx": item['idx']
                } for item in dates_confirmed]
            )
            print(f"✅ Sincronizados {len(dates_confirmed)} fragmentos en ChromaDB.")

            return {"text": text, "filename": file.filename, "status": "Ready for RAG"}
        else:
            print("❌ ERROR: No hay datos para enviar a Chroma. Revisa save_document_rag.")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


