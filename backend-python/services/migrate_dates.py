import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
import mysql.connector
from urllib.parse import urlparse
from dotenv import load_dotenv

from config import DB_PATH

load_dotenv()

client = chromadb.PersistentClient(path=DB_PATH)
col = client.get_or_create_collection(name="document_chunk")

# --- CONEXIÓN A MYSQL ---
try:
    db_url_env = os.getenv("DATABASE_URL")

    url = urlparse(db_url_env)

    db = mysql.connector.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        port=url.port or 3306,
        database=url.path[1:]
    )

    cursor = db.cursor(dictionary=True)

    print("🔌 Conectado a MySQL. Extrayendo datos...")
    cursor.execute("SELECT id, chat_id, chunk_content, idx, file_name FROM document_chunks")
    filas = cursor.fetchall()

    if not filas:
        print("⚠️ No hay datos en la tabla 'document_chunks'.")
    else:
        print(f"📦 Migrando {len(filas)} fragmentos...")

        # Preparamos las listas (Chroma es más rápido si le mandas todo junto)
        ids_sql = [str(f['id']) for f in filas]
        textos = [f['chunk_content'] for f in filas]
        metadatos = [{"chat_id": f['chat_id'], "idx": f['idx'], "file_name": f['file_name']} for f in filas]

        # Insertar en Chroma
        col.add(
            ids=ids_sql,
            documents=textos,
            metadatas=metadatos
        )

        print(f"✅ ¡TERMINADO! ChromaDB ahora tiene {col.count()} registros.")

except Exception as e:
    print(f"💥 Error durante la migración: {e}")
finally:
    if 'db' in locals(): db.close()