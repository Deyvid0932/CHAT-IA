import mysql.connector
import os
from dotenv import load_dotenv
from urllib.parse import urlparse  # Importante para romper la URL
from sentence_transformers import SentenceTransformer

# Carga el archivo .env
load_dotenv()
model = SentenceTransformer('all-MiniLM-L6-v2')

def obtener_conexion():
    """Conecta a MySQL usando una única DB_URL del archivo .env"""
    try:
        # Extraemos la URL del entorno
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("No se encontró DATABASE_URL en el archivo .env")

        # Parseamos la URL para obtener los datos por separado
        url = urlparse(db_url)

        return mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            port=url.port or 3306,
            database=url.path[1:]  # Quitamos la '/' inicial del nombre de la DB
        )
    except Exception as e:
        print(f"❌ Error de conexión con DB_URL: {e}")
        return None


def crear_tablas():
    """Crea las tablas necesarias si no existen y asegura que las columnas existan."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        # Tabla para Sesiones de Chat
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones_chat (
            id VARCHAR(50) PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)

        # Tabla para PDFs asociada a un Chat
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos_pdf (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(50),
            nombre_archivo VARCHAR(255) NOT NULL,
            contenido_texto LONGTEXT NOT NULL,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Asegurar que chat_id existe en documentos_pdf
        try:
            cursor.execute("ALTER TABLE documentos_pdf ADD COLUMN chat_id VARCHAR(50)")
        except:
            pass

        # Intentar añadir la foreign key para documentos_pdf
        try:
            cursor.execute("""
                ALTER TABLE documentos_pdf 
                ADD CONSTRAINT fk_chat_pdf 
                FOREIGN KEY (chat_id) REFERENCES sesiones_chat(id) 
                ON DELETE CASCADE
            """)
        except:
            pass

        # Tabla para Historial de Mensajes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_chat (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(50),
            rol ENUM('user', 'assistant') NOT NULL,
            contenido TEXT NOT NULL,
            nombre_archivo VARCHAR(255),
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES sesiones_chat(id) ON DELETE CASCADE
        )
        """)
        
        # Asegurar que nombre_archivo existe en historial_chat
        try:
            cursor.execute("ALTER TABLE historial_chat ADD COLUMN nombre_archivo VARCHAR(255)")
        except:
            pass

        # Tabla para Chunks de Documentos (RAG)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos_chunks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(50),
            nombre_archivo VARCHAR(255) NOT NULL,
            contenido_chunk TEXT NOT NULL,
            indice INT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES sesiones_chat(id) ON DELETE CASCADE
        )
        """)
            
        db.commit()
        cursor.close()
        db.close()
        print("✅ Base de datos inicializada y esquema verificado.")


def guardar_mensaje(chat_id, rol, contenido, nombre_archivo=None):
    """Guarda un mensaje individual en el historial con nombre de archivo opcional. Crea la sesión si no existe."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        
        # Verificar si la sesión existe
        cursor.execute("SELECT id FROM sesiones_chat WHERE id = %s", (chat_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO sesiones_chat (id, titulo) VALUES (%s, %s)", (chat_id, "Nueva conversación"))
            
        query = "INSERT INTO historial_chat (chat_id, rol, contenido, nombre_archivo) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (chat_id, rol, contenido, nombre_archivo))
        db.commit()
        cursor.close()
        db.close()

def crear_sesion_chat(chat_id, titulo):
    """Crea una nueva sesión de chat en la DB. Ignora si ya existe."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        # Usamos INSERT IGNORE para evitar errores si ya se creó automáticamente
        query = "INSERT IGNORE INTO sesiones_chat (id, titulo) VALUES (%s, %s)"
        cursor.execute(query, (chat_id, titulo))
        db.commit()
        cursor.close()
        db.close()

def actualizar_titulo_chat(chat_id, nuevo_titulo):
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        query = "UPDATE sesiones_chat SET titulo = %s WHERE id = %s"
        cursor.execute(query, (nuevo_titulo, chat_id))
        db.commit()
        cursor.close()
        db.close()

def eliminar_sesion_chat(chat_id):
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        query = "DELETE FROM sesiones_chat WHERE id = %s"
        cursor.execute(query, (chat_id,))
        db.commit()
        cursor.close()
        db.close()

def eliminar_todos_los_chats():
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM sesiones_chat")
        db.commit()
        cursor.close()
        db.close()

def obtener_chats():
    """Obtiene todas las sesiones de chat con sus mensajes."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor(dictionary=True)
        # Obtenemos las sesiones
        cursor.execute("SELECT * FROM sesiones_chat ORDER BY fecha_actualizacion DESC")
        sesiones = cursor.fetchall()
        
        for sesion in sesiones:
            # Obtenemos los mensajes de cada sesión
            cursor.execute("SELECT id, rol, contenido, nombre_archivo FROM historial_chat WHERE chat_id = %s ORDER BY fecha ASC", (sesion['id'],))
            mensajes = cursor.fetchall()
            sesion['messages'] = [{
                "id": str(m['id']), 
                "role": m['rol'], 
                "content": m['contenido'],
                "fileName": m['nombre_archivo']
            } for m in mensajes]
            
        cursor.close()
        db.close()
        return sesiones
    return []


def guardar_documento(chat_id, nombre, contenido):
    """Guarda un documento PDF. Crea la sesión si no existe para evitar errores de FK."""
    db = obtener_conexion()
    if db:
        try:
            cursor = db.cursor()

            # Verificar si la sesión existe antes de insertar el PDF
            cursor.execute("SELECT id FROM sesiones_chat WHERE id = %s", (chat_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO sesiones_chat (id, titulo) VALUES (%s, %s)", (chat_id, "Nueva conversación"))

            query_doc = "INSERT INTO documentos_pdf (chat_id, nombre_archivo, contenido_texto) VALUES (%s, %s, %s)"
            cursor.execute(query_doc, (chat_id, nombre, contenido))

            db.commit()
            print(f"✅ PDF '{nombre}' guardado y sesión verificada para el chat {chat_id}.")
            cursor.close()
        except Exception as e:
            print(f"❌ Error al guardar documento: {e}")
        finally:
            db.close()


def guardar_documento_rag(chat_id, nombre, texto_completo):
    print(f"DEBUG: Longitud del texto recibido: {len(texto_completo)} caracteres")
    db = obtener_conexion()
    if db:
        try:
            cursor = db.cursor()

            # Verificar si la sesión existe antes de insertar el PDF
            cursor.execute("SELECT id FROM sesiones_chat WHERE id = %s", (chat_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO sesiones_chat (id, titulo) VALUES (%s, %s)", (chat_id, "Nueva conversación"))

            # 1. Picar el texto (Chunking)
            # Dividimos por bloques de 800 caracteres
            chunks = [texto_completo[i:i + 800] for i in range(0, len(texto_completo), 800)]

            # 2. Guardar cada trozo
            for i, chunk_text in enumerate(chunks):
                query = """
                INSERT INTO documentos_chunks (chat_id, nombre_archivo, contenido_chunk, indice)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (chat_id, nombre, chunk_text, i))

            db.commit()
            print(f"✅ Documento '{nombre}' procesado para RAG y guardado ({len(chunks)} chunks) para el chat {chat_id}.")
            cursor.close()
        except Exception as e:
            print(f"❌ Error al guardar documento RAG: {e}")
        finally:
            db.close()

def obtener_todos_los_documentos(chat_id, nombre_archivo=None):
    """Recupera los PDFs guardados para este chat. Si se da un nombre, recupera solo ese."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()

        if nombre_archivo:
            query = """
                    SELECT nombre_archivo, contenido_texto
                    FROM documentos_pdf
                    WHERE chat_id = %s AND nombre_archivo = %s
                    LIMIT 1
                    """
            cursor.execute(query, (chat_id, nombre_archivo))
        else:
            query = """
                    SELECT nombre_archivo, contenido_texto
                    FROM documentos_pdf
                    WHERE chat_id = %s
                    ORDER BY fecha_subida DESC
                    """
            cursor.execute(query, (chat_id,))
            
        rows = cursor.fetchall()

        contexto = ""
        for row in rows:
            contexto += f"\n--- ARCHIVO: {row[0]} ---\n{row[1]}\n"

        cursor.close()
        db.close()

        return contexto

    return ""


def obtener_contexto_para_chat(chat_id):
    """Obtiene el texto relacionado a la conversación actual, incluyendo chunks si existen."""
    db = obtener_conexion()
    if not db:
        return ""

    cursor = db.cursor(dictionary=True)
    # 1) Obtener PDF más reciente
    pdf_query = "SELECT nombre_archivo, contenido_texto FROM documentos_pdf WHERE chat_id = %s ORDER BY fecha_subida DESC LIMIT 1"
    cursor.execute(pdf_query, (chat_id,))
    pdf_row = cursor.fetchone()
    pdf_text = pdf_row.get("contenido_texto") if pdf_row else ""
    pdf_name = pdf_row.get("nombre_archivo") if pdf_row else None

    # 2) Obtener chunks
    chunk_query = "SELECT nombre_archivo, contenido_chunk, indice FROM documentos_chunks WHERE chat_id = %s ORDER BY indice ASC"
    cursor.execute(chunk_query, (chat_id,))
    chunks = cursor.fetchall()

    contexto = ""
    if chunks:
        for c in chunks:
            contexto += f"\n--- ARCHIVO: {c['nombre_archivo']} (chunk {c['indice']}) ---\n{c['contenido_chunk']}"
        contexto = contexto.strip()
    if not contexto and pdf_text:
        contexto = pdf_text
    elif contexto and pdf_text:
        contexto = f"{contexto}\n\nDATOS DEL ARCHIVO (PDF reciente: {pdf_name}):\n{pdf_text}"

    cursor.close()
    db.close()
    return contexto
