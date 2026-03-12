import mysql.connector
import os
import chromadb
from dotenv import load_dotenv
from urllib.parse import urlparse

from config import DB_PATH

load_dotenv()

def get_connection():
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not found in .env file")

        url = urlparse(db_url)

        return mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            port=url.port or 3306,
            database=url.path[1:]
        )
    except Exception as e:
        print(f"❌ Connection error with DB_URL: {e}")
        return None


def create_tables():
    db = get_connection()
    if db:
        cursor = db.cursor()

        # 1. Tabla de Sesiones (La base de todo)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """)

        # 2. Tabla de PDFs (Con la relación integrada)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(50),
            file_name VARCHAR(255) NOT NULL,
            text_content LONGTEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_pdf_session FOREIGN KEY (chat_id) 
                REFERENCES chat_sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
        """)

        # 3. Tabla de Historial
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(50),
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            file_name VARCHAR(255),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_history_session FOREIGN KEY (chat_id) 
                REFERENCES chat_sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
        """)

        # 4. Tabla de Chunks
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(50),
            file_name VARCHAR(255) NOT NULL,
            chunk_content TEXT NOT NULL,
            idx INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_chunks_session FOREIGN KEY (chat_id) 
                REFERENCES chat_sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
        """)

        db.commit()
        cursor.close()
        db.close()
        print("✅ Base de datos sincronizada con relaciones CASCADE.")


def save_message(chat_id, role, content, file_name=None):
    db = get_connection()
    if db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM chat_sessions WHERE id = %s", (chat_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO chat_sessions (id, title) VALUES (%s, %s)", (chat_id, "New conversation"))
            
        query = "INSERT INTO chat_history (chat_id, role, content, file_name) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (chat_id, role, content, file_name))
        db.commit()
        cursor.close()
        db.close()

def create_chat_session(chat_id, title):
    db = get_connection()
    if db:
        cursor = db.cursor()
        query = "INSERT IGNORE INTO chat_sessions (id, title) VALUES (%s, %s)"
        cursor.execute(query, (chat_id, title))
        db.commit()
        cursor.close()
        db.close()

def update_chat_title(chat_id, new_title):
    db = get_connection()
    if db:
        cursor = db.cursor()
        query = "UPDATE chat_sessions SET title = %s WHERE id = %s"
        cursor.execute(query, (new_title, chat_id))
        db.commit()
        cursor.close()
        db.close()

def delete_chat_session(chat_id):
    db = get_connection()
    if db:
        cursor = db.cursor()
        query = "DELETE FROM chat_sessions WHERE id = %s"
        cursor.execute(query, (chat_id,))
        db.commit()
        cursor.close()
        db.close()

def delete_all_chats():
    db = get_connection()
    if db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM chat_sessions")
        db.commit()
        cursor.close()
        db.close()

def get_chats():
    db = get_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chat_sessions ORDER BY updated_at DESC")
        raw_sessions = cursor.fetchall()
        
        sessions = []
        for s in raw_sessions:
            session = {
                "id": s.get('id'),
                "title": s.get('title') or s.get('titulo'),
                "created_at": s.get('created_at') or s.get('fecha_creacion'),
                "updated_at": s.get('updated_at') or s.get('fecha_actualizacion'),
            }
            
            cursor.execute("SELECT id, role, content, file_name FROM chat_history WHERE chat_id = %s ORDER BY date ASC", (session['id'],))
            messages = cursor.fetchall()
            session['messages'] = [{
                "id": str(m['id']), 
                "role": m['role'], 
                "content": m['content'],
                "fileName": m['file_name']
            } for m in messages]
            sessions.append(session)
            
        cursor.close()
        db.close()
        return sessions
    return []


def save_document(chat_id, name, content):
    db = get_connection()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id FROM chat_sessions WHERE id = %s", (chat_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO chat_sessions (id, title) VALUES (%s, %s)", (chat_id, "New conversation"))

            query_doc = "INSERT INTO pdf_documents (chat_id, file_name, text_content) VALUES (%s, %s, %s)"
            cursor.execute(query_doc, (chat_id, name, content))

            db.commit()
            print(f" PDF '{name}' saved and session verified for chat {chat_id}.")
            cursor.close()
        except Exception as e:
            print(f" Error saving document: {e}")
        finally:
            db.close()


def save_document_rag(chat_id, name, full_text):
    db = get_connection()
    if db:
        try:
            cursor = db.cursor()

            cursor.execute("SELECT id FROM chat_sessions WHERE id = %s", (chat_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO chat_sessions (id, title) VALUES (%s, %s)", (chat_id, "New conversation"))

            chunks = [full_text[i:i + 800] for i in range(0, len(full_text), 800)]

            db.commit()

            details_save = save_chunks_en_mysql(chunks, chat_id, name)

            return details_save


        except Exception as e:
            print(f" Error saving RAG document: {e}")

        finally:
            cursor.close()
            db.close()

def save_chunks_en_mysql(chunks, chat_id, file_name):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    details_save = []

    try:
        for idx, content in enumerate(chunks):
            query = "INSERT INTO document_chunks (chat_id, chunk_content, idx, file_name) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (chat_id, content, idx, file_name))

            current_id = cursor.lastrowid

            details_save.append({
            "id": current_id,
            "content": content,
            "idx": idx
            })

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")

    finally:
        db.close()

    return details_save

def delete_pdf_db(chat_id, file_name):
    db = get_connection()
    if db:
        try:
            cursor = db.cursor()

            cursor.execute(
                "DELETE FROM document_chunks WHERE chat_id = %s AND TRIM(file_name) = TRIM(%s)",
                (chat_id, file_name)
            )
            chunks_borrados = cursor.rowcount

            # 2. Borramos el padre (pdf_documents)
            cursor.execute(
                "DELETE FROM pdf_documents WHERE chat_id = %s AND TRIM(file_name) = TRIM(%s)",
                (chat_id, file_name)
            )
            pdf_borrado = cursor.rowcount
            
            db.commit()

            if pdf_borrado > 0:
                print(f" Éxito: Se borró el PDF y {chunks_borrados} chunks.")
                return True
            else:
                print(f" El PDF no se borró. ¿El nombre '{file_name}' es exacto?")
                return False

        except Exception as e:
            print(f" Error deleting PDF: {e}")
            return False
        finally:
            db.close()

            try:
                client = chromadb.PersistentClient(path=DB_PATH)
                col = client.get_collection(name="document_chunks")

                col.delete(
                    where={"chat_id": str(chat_id), "file_name": file_name}
                )
                print(f" ChromaDB: Vectores eliminados para {file_name}")
            except Exception as e:
                print(f" Error en ChromaDB: {e}")
    return False


def get_all_documents(chat_id, file_name=None):
    db = get_connection()
    if db:
        cursor = db.cursor()

        if file_name:
            query = """
                    SELECT file_name, text_content
                    FROM pdf_documents
                    WHERE chat_id = %s AND file_name = %s
                    LIMIT 1
                    """
            cursor.execute(query, (chat_id, file_name))
        else:
            query = """
                    SELECT file_name, text_content
                    FROM pdf_documents
                    WHERE chat_id = %s
                    ORDER BY upload_date DESC
                    """
            cursor.execute(query, (chat_id,))
            
        rows = cursor.fetchall()

        context = ""
        for row in rows:
            context += f"\n--- FILE: {row[0]} ---\n{row[1]}\n"

        cursor.close()
        db.close()

        return context

    return ""


def get_chat_context(chat_id):
    db = get_connection()
    if not db:
        return ""

    cursor = db.cursor(dictionary=True)
    pdf_query = "SELECT file_name, text_content FROM pdf_documents WHERE chat_id = %s ORDER BY upload_date DESC LIMIT 1"
    cursor.execute(pdf_query, (chat_id,))
    pdf_row = cursor.fetchone()
    pdf_text = pdf_row.get("text_content") if pdf_row else ""
    pdf_name = pdf_row.get("file_name") if pdf_row else None

    chunk_query = "SELECT file_name, chunk_content, idx FROM document_chunks WHERE chat_id = %s ORDER BY idx ASC"
    cursor.execute(chunk_query, (chat_id,))
    chunks = cursor.fetchall()

    context = ""
    if chunks:
        for c in chunks:
            context += f"\n--- FILE: {c['file_name']} (chunk {c['idx']}) ---\n{c['chunk_content']}"
        context = context.strip()
    if not context and pdf_text:
        context = pdf_text
    elif context and pdf_text:
        context = f"{context}\n\nFILE DATA (recent PDF: {pdf_name}):\n{pdf_text}"

    cursor.close()
    db.close()
    return context
