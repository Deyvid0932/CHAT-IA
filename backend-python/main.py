import sys
import os

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import pdf, chat
from services.database import obtener_conexion, crear_tablas

load_dotenv()
app = FastAPI(title="IA_PDF Backend")

@app.on_event("startup")
def verificar_conexion_db():
    print("🔍 Verificando conexión a la base de datos...")
    db = obtener_conexion()
    if db and db.is_connected():
        print("✅ ¡Conexión exitosa a MySQL! La memoria del RAG está lista.")
        crear_tablas()  # Aseguramos que la tabla documentos_pdf exista
        db.close()
    else:
        print("❌ ERROR: No se pudo conectar a MySQL. Revisa tu DATABASE_URL en el .env")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(pdf.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
