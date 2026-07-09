from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from app.schemas.interaction import InteractionBase


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatMessageOut(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    reply: str
    interaction: InteractionBase
    tool_used: Optional[str] = None
    is_valid_for_save: bool = False
    missing_fields: List[str] = []
    history: List[ChatMessageOut] = []
