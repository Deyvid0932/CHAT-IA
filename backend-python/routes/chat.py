from fastapi import APIRouter, HTTPException
from services.ollama_service import get_ollama_chat_response
from services.database import (
    obtener_todos_los_documentos, 
    guardar_mensaje, 
    obtener_chats, 
    crear_sesion_chat,
    eliminar_sesion_chat,
    eliminar_todos_los_chats,
    actualizar_titulo_chat,
    limpiar_pdf_sesion # IMPORTANTE
)

router = APIRouter()

@router.get("/chats")
async def get_chats():
    """Retorna todas las sesiones de chat con sus mensajes."""
    return {"chats": obtener_chats()}

@router.post("/chats")
async def create_chat(data: dict):
    chat_id = data.get("id")
    titulo = data.get("title", "Nueva conversación")
    crear_sesion_chat(chat_id, titulo)
    return {"status": "success"}

@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    eliminar_sesion_chat(chat_id)
    return {"status": "success"}

@router.delete("/chats")
async def clear_chats():
    eliminar_todos_los_chats()
    return {"status": "success"}

@router.post("/chat")
async def chat_endpoint(data: dict):
    pregunta = data.get("message")
    chat_id = data.get("chatId")
    file_name = data.get("fileName") # Recibimos el nombre del archivo

    if not chat_id:
        raise HTTPException(status_code=400, detail="chatId es requerido")

    # Recuperamos los documentos de la DB para este chat específico
    contexto_db = obtener_todos_los_documentos(chat_id)

    # Si el frontend envía algo extra, lo sumamos
    contexto_extra = data.get("pdfContext", "")

    contexto_final = f"{contexto_db}\n{contexto_extra}".strip()

    conciseness = data.get("conciseness", "balanced")
    speed = data.get("speed", "normal")

    respuesta = get_ollama_chat_response(pregunta, contexto_final, conciseness, speed)

    # GUARDAR EN LA BASE DE DATOS con el nombre del archivo si existe
    guardar_mensaje(chat_id, "user", pregunta, file_name)
    guardar_mensaje(chat_id, "assistant", respuesta)

    # LIMPIAR EL PDF DE LA SESIÓN para evitar autocarga en el futuro
    limpiar_pdf_sesion(chat_id)

    # Actualizar título si es el primer mensaje
    actualizar_titulo_chat(chat_id, pregunta[:30] + "...")

    return {"response": respuesta}
