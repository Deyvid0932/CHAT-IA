from fastapi import APIRouter, HTTPException, Request
from services.ollama_service import get_ollama_chat_response, search_relevant_chunks
from services.database import (
    save_message, 
    get_chats, 
    create_chat_session,
    delete_chat_session,
    delete_all_chats,
    update_chat_title,
)

router = APIRouter()

@router.get("/chats")
async def fetch_chats():
    return {"chats": get_chats()}

@router.post("/chats")
async def create_chat(data: dict):
    chat_id = data.get("id")
    title = data.get("title", "New conversation")
    create_chat_session(chat_id, title)
    return {"status": "success"}

@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    delete_chat_session(chat_id)
    return {"status": "success"}

@router.delete("/chats")
async def clear_chats():
    delete_all_chats()
    return {"status": "success"}

@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    question = data.get("message")
    chat_id = data.get("chatId")
    file_name = data.get("fileName") 

    if not chat_id:
        raise HTTPException(status_code=400, detail="chatId is required")

    conciseness = data.get("conciseness", "balanced")
    speed = data.get("speed", "normal")

    if data.get("resetContext"):
        final_context = ""
    else:
        final_context = search_relevant_chunks(chat_id, question)

    response = get_ollama_chat_response(question, final_context, conciseness, speed)

    save_message(chat_id, "user", question, file_name)
    save_message(chat_id, "assistant", response)

    update_chat_title(chat_id, question[:30] + "...")

    return {"response": response}