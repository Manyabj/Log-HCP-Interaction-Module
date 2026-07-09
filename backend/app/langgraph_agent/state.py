"""
Shared state object that flows through every node of the LangGraph graph.
"""
from typing import Any, Dict, List, Optional, TypedDict


class InteractionState(TypedDict, total=False):
    # Conversation
    session_id: str
    user_message: str
    conversation_history: List[Dict[str, str]]  # [{"role": ..., "content": ...}]

    # Structured interaction data (mirrors the Redux form state on the frontend)
    interaction: Dict[str, Any]

    # Routing / intermediate reasoning
    intent: Optional[str]           # log | edit | clear_field | summarize | validate | chat
    extracted_fields: Dict[str, Any]
    clear_targets: List[str]

    # Output
    tool_used: Optional[str]
    reply: Optional[str]
    is_valid_for_save: bool
    missing_fields: List[str]


def empty_interaction() -> Dict[str, Any]:
    return {
        "hcp_name": None,
        "interaction_type": None,
        "interaction_date": None,
        "interaction_time": None,
        "attendees": [],
        "topics": [],
        "product": None,
        "sentiment": None,
        "materials": [],
        "notes": None,
        "summary": None,
        "status": "draft",
    }
