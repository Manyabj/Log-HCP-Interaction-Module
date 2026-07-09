from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.interaction import Interaction
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageOut
from app.schemas.interaction import InteractionBase
from app.langgraph_agent.graph import agent_graph
from app.langgraph_agent.state import empty_interaction

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_or_create_draft(db: Session, session_id: str) -> Interaction:
    draft = (
        db.query(Interaction)
        .filter(Interaction.session_id == session_id, Interaction.status != "saved")
        .order_by(Interaction.created_at.desc())
        .first()
    )
    if draft is None:
        draft = Interaction(session_id=session_id, **empty_interaction())
        db.add(draft)
        db.commit()
        db.refresh(draft)
    return draft


def _interaction_to_dict(interaction: Interaction) -> dict:
    return {
        "hcp_name": interaction.hcp_name,
        "interaction_type": interaction.interaction_type,
        "interaction_date": interaction.interaction_date,
        "interaction_time": interaction.interaction_time,
        "attendees": interaction.attendees or [],
        "topics": interaction.topics or [],
        "product": interaction.product,
        "sentiment": interaction.sentiment,
        "materials": interaction.materials or [],
        "notes": interaction.notes,
        "summary": interaction.summary,
        "status": interaction.status,
    }


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    draft = _get_or_create_draft(db, request.session_id)

    # Load prior conversation for context
    prior_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == request.session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    conversation_history = [{"role": m.role, "content": m.content} for m in prior_messages]

    # Persist the incoming user message
    user_msg = ChatMessage(session_id=request.session_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # Run the LangGraph agent
    try:
        result_state = agent_graph.invoke({
            "session_id": request.session_id,
            "user_message": request.message,
            "conversation_history": conversation_history,
            "interaction": _interaction_to_dict(draft),
        })
    except Exception as e:
        import traceback
        exc_text = traceback.format_exc()
        traceback.print_exc()
        print("ERROR:", repr(e))
        raise HTTPException(status_code=500, detail={"error": str(e), "trace": exc_text})
    updated_interaction = result_state["interaction"]
    reply = result_state.get("reply", "")

    # Persist assistant reply
    assistant_msg = ChatMessage(session_id=request.session_id, role="assistant", content=reply)
    db.add(assistant_msg)

    # Persist updated structured interaction back onto the draft row
    for key, value in updated_interaction.items():
        setattr(draft, key, value)
    db.add(draft)
    db.commit()
    db.refresh(draft)

    history_out = [
        ChatMessageOut(role=m.role, content=m.content) for m in prior_messages
    ] + [ChatMessageOut(role="user", content=request.message), ChatMessageOut(role="assistant", content=reply)]

    return ChatResponse(
        reply=reply,
        interaction=InteractionBase(**_interaction_to_dict(draft)),
        tool_used=result_state.get("tool_used"),
        is_valid_for_save=result_state.get("is_valid_for_save", False),
        missing_fields=result_state.get("missing_fields", []),
        history=history_out,
    )
