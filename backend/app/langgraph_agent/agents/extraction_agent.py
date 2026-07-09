"""
Router / intent-classification agent.

Every incoming chat message is first classified into exactly one intent
so the LangGraph graph knows which tool node to route to. This is done
entirely via the Groq LLM — no keyword matching or hardcoded rules.
"""
import json
from typing import Any, Dict

from app.langgraph_agent.llm import call_json_llm

SYSTEM_PROMPT = """You are the routing brain of an AI CRM assistant for logging \
Healthcare Professional (HCP) interactions. Classify the rep's latest message into \
exactly one intent:

- "log"       -> the rep is describing a new interaction, or adding new information to it \
                 (first-time description of a meeting/call, or adding more detail such as \
                 topics/materials/attendees that weren't corrections of existing data).
- "edit"      -> the rep is CORRECTING information that was already captured \
                 (e.g. "Actually it was Dr. John", "No, sentiment was negative").
- "clear"     -> the rep wants to remove/clear a previously captured field or item \
                 (e.g. "remove the brochures", "clear the notes").
- "summarize" -> the rep explicitly asks for a summary of the interaction.
- "save"      -> the rep wants to save/submit/finalize the interaction \
                 (e.g. "save this", "submit", "that's all, log it").
- "chat"      -> anything else / general question that doesn't change the form.

Return ONLY JSON: { "intent": "<one of: log, edit, clear, summarize, save, chat>" }
"""


def classify_intent(user_message: str, current_interaction: Dict[str, Any]) -> str:
    prompt = (
        f"CURRENT_STATE:\n{json.dumps(current_interaction, indent=2)}\n\n"
        f"REP_MESSAGE:\n{user_message}"
    )
    result = call_json_llm(SYSTEM_PROMPT, prompt)
    intent = result.get("intent", "log")
    if intent not in {"log", "edit", "clear", "summarize", "save", "chat"}:
        intent = "log"
    return intent
