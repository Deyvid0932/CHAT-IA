import mysql.connector
import os
from dotenv import load_dotenv
from urllib.parse import urlparse  # Importante para romper la URL

# Carga el archivo .env
load_dotenv()


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
    """Crea las tablas necesarias si no existen."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        # Tabla para Sesiones de Chat
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones_chat (
            id VARCHAR(50) PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            pdf_content LONGTEXT,
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

        # Intentar añadir la columna chat_id y la foreign key si no existen
        try:
            cursor.execute("ALTER TABLE documentos_pdf ADD COLUMN chat_id VARCHAR(50)")
        except:
            pass # Ya existe

        try:
            cursor.execute("""
                ALTER TABLE documentos_pdf 
                ADD CONSTRAINT fk_chat_pdf 
                FOREIGN KEY (chat_id) REFERENCES sesiones_chat(id) 
                ON DELETE CASCADE
            """)
        except:
            pass # Ya existe o error

        # Tabla para Historial de Mensajes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_chat (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(50),
            rol ENUM('user', 'assistant') NOT NULL,
            contenido TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES sesiones_chat(id) ON DELETE CASCADE
        )
        """)
        db.commit()
        cursor.close()
        db.close()
        print("✅ Base de datos inicializada (Tablas multi-chat aseguradas).")


def guardar_mensaje(chat_id, rol, contenido):
    """Guarda un mensaje individual en el historial."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        query = "INSERT INTO historial_chat (chat_id, rol, contenido) VALUES (%s, %s, %s)"
        cursor.execute(query, (chat_id, rol, contenido))
        db.commit()
        cursor.close()
        db.close()

def crear_sesion_chat(chat_id, titulo):
    """Crea una nueva sesión de chat en la DB."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        query = "INSERT INTO sesiones_chat (id, titulo) VALUES (%s, %s)"
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
            cursor.execute("SELECT id, rol, contenido FROM historial_chat WHERE chat_id = %s ORDER BY fecha ASC", (sesion['id'],))
            mensajes = cursor.fetchall()
            sesion['messages'] = [{"id": str(m['id']), "role": m['rol'], "content": m['contenido']} for m in mensajes]
            
        cursor.close()
        db.close()
        return sesiones
    return []


def guardar_documento(chat_id, nombre, contenido):
    """Guarda el texto en MySQL asociado a un chat específico"""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()
        query = "INSERT INTO documentos_pdf (chat_id, nombre_archivo, contenido_texto) VALUES (%s, %s, %s)"
        cursor.execute(query, (chat_id, nombre, contenido))
        db.commit()
        cursor.close()
        db.close()
        print(f"✅ Memoria guardada exitosamente para el chat {chat_id}.")


def obtener_todos_los_documentos(chat_id):
    """Recupera los PDFs guardados. Si se pasa chat_id, filtra por ese chat."""
    db = obtener_conexion()
    if db:
        cursor = db.cursor()

        query = """
                SELECT nombre_archivo, contenido_texto
                FROM documentos_pdf
                WHERE chat_id = %s
                ORDER BY fecha_subida DESC LIMIT 1
                """

        cursor.execute(query, (chat_id,))

        row = cursor.fetchone()

        if row:
            # MANTENER: El formato de retorno, pero solo para un archivo
            contexto = f"\n--- ARCHIVO ACTUAL: {row[0]} ---\n{row[1]}\n"
        else:
            contexto = ""

        cursor.close()  # MANTENER: Siempre cierra el cursor
        db.close()  # MANTENER: Siempre cierra la conexión

        return contexto

    return ""


def obtener_contexto_para_chat(chat_id):
    """Obtiene solo el texto relacionado a la conversación actual"""
    db = obtener_conexion()
    if not db: return ""

    cursor = db.cursor()
    # Filtramos estrictamente por el chat_id
    query = "SELECT contenido_texto FROM documentos_pdf WHERE chat_id = %s ORDER BY fecha_subida DESC LIMIT 1"
    cursor.execute(query, (chat_id,))

    resultado = cursor.fetchone()
    cursor.close()
    db.close()

    return resultado[0] if resultado else ""