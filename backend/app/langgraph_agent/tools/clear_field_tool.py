"""
Tool 3 — ClearFieldTool

Handles removal requests such as: "Remove the brochures." or
"Clear the notes field." Only the requested field(s) are cleared;
every other field in the interaction remains untouched.
"""
import json
from typing import Any, Dict, List, Tuple

from app.langgraph_agent.llm import call_json_llm

VALID_FIELDS = [
    "hcp_name", "interaction_type", "interaction_date", "interaction_time",
    "attendees", "topics", "product", "sentiment", "materials", "notes",
]

LIST_FIELDS = {"attendees", "topics", "materials"}

SYSTEM_PROMPT = """You are a clinical CRM field-removal engine. The rep wants to clear or \
remove one or more fields from a previously logged HCP interaction.

Valid field names: hcp_name, interaction_type, interaction_date, interaction_time, \
attendees, topics, product, sentiment, materials, notes.

Given the rep's message, decide which of these fields should be cleared. Return ONLY:
{ "fields_to_clear": ["<field_name>", ...] }

If the rep mentions a specific value inside a list field (e.g. "remove the brochure" when \
materials might contain several items), still just clear/target the whole "materials" field \
unless the message clearly says to remove just one item while keeping others — in that case \
return { "fields_to_clear": [], "remove_list_items": { "materials": ["Brochure"] } } instead.
Respond with raw JSON only.
"""


def run(user_message: str, current_interaction: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    prompt = (
        f"CURRENT_STATE:\n{json.dumps(current_interaction, indent=2)}\n\n"
        f"REP_MESSAGE:\n{user_message}"
    )
    result = call_json_llm(SYSTEM_PROMPT, prompt)

    updated = dict(current_interaction)
    cleared: List[str] = []

    fields_to_clear = [f for f in result.get("fields_to_clear", []) if f in VALID_FIELDS]
    for field in fields_to_clear:
        updated[field] = [] if field in LIST_FIELDS else None
        cleared.append(field)

    remove_items = result.get("remove_list_items", {}) or {}
    for field, items in remove_items.items():
        if field in LIST_FIELDS and field in updated:
            existing = updated.get(field) or []
            updated[field] = [i for i in existing if i not in items]
            cleared.append(field)

    updated["status"] = "draft"
    return updated, cleared
