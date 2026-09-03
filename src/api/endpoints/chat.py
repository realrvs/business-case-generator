# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel

from src.services.business_case_chat import BusinessCaseChat
from src.services.business_case_generator import BusinessCaseGenerator

router = APIRouter(prefix="/business-case", tags=["business-case"])

class ChatRequest(BaseModel):
    project_name: str
    message: str

class StartChatRequest(BaseModel):
    project_name: str
    business_case: Dict[str, Any]

# Хранилище сессий чата
chat_sessions = {}

@router.post("/chat/start")
async def start_chat(request: StartChatRequest):
    chat = BusinessCaseChat()
    result = chat.start_chat(request.project_name, request.business_case)
    chat_sessions[request.project_name] = chat
    return result

@router.post("/chat/message")
async def send_message(request: ChatRequest):
    if request.project_name not in chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден. Сначала запустите чат."
        )
    
    chat = chat_sessions[request.project_name]
    result = chat.send_message(request.message)
    return result

@router.get("/chat/history/{project_name}")
async def get_chat_history(project_name: str):
    if project_name not in chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )
    
    chat = chat_sessions[project_name]
    return {
        "project_name": project_name,
        "history": chat.history,
        "context": chat.context
    }

@router.delete("/chat/{project_name}")
async def clear_chat(project_name: str):
    if project_name in chat_sessions:
        del chat_sessions[project_name]
    return {"message": "Чат очищен"}
