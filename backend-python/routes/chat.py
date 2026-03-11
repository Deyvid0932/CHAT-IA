from fastapi import APIRouter, HTTPException
from services.ollama_service import get_ollama_chat_response, buscar_chunks_relevantes
from services.database import (
    guardar_mensaje, 
    obtener_chats, 
    crear_sesion_chat,
    eliminar_sesion_chat,
    eliminar_todos_los_chats,
    actualizar_titulo_chat,
)

router = APIRouter()

@router.get("/chats")
async def get_chats():
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

    conciseness = data.get("conciseness", "balanced")
    speed = data.get("speed", "normal")

    if data.get("resetContext"):
        contexto_final = ""
    else:
        # Usamos RAG para buscar chunks relevantes en lugar de todo el texto
        contexto_final = buscar_chunks_relevantes(chat_id, pregunta)

    respuesta = get_ollama_chat_response(pregunta, contexto_final, conciseness, speed)

    # GUARDAR EN LA BASE DE DATOS con el nombre del archivo si existe
    guardar_mensaje(chat_id, "user", pregunta, file_name)
    guardar_mensaje(chat_id, "assistant", respuesta)

    # Actualizar título si es el primer mensaje (basado en la pregunta)
    # Solo actualizamos si es un chat nuevo o no tiene título significativo todavía
    actualizar_titulo_chat(chat_id, pregunta[:30] + "...")

    return {"response": respuesta}