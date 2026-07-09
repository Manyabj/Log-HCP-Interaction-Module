"""
Tool 2 — EditInteractionTool

Handles corrections such as:
  "Actually the doctor was Dr. John and the sentiment was negative."

Only the fields the rep is explicitly correcting are changed —
everything else in the current interaction is left exactly as-is.
The LLM is given the CURRENT state so it can reason about what
"changed" actually means (e.g. it must not re-emit unrelated fields).
"""
import json
from typing import Any, Dict

from app.langgraph_agent.llm import call_json_llm

SYSTEM_PROMPT = """You are a clinical CRM correction engine. The rep has already logged an \
HCP interaction (shown below as CURRENT_STATE) and is now sending a correction message.

Identify ONLY the fields that the rep is explicitly changing in their new message. \
Do NOT include a field in your output unless the message clearly changes it.

Valid field names: hcp_name, interaction_type, interaction_date, interaction_time, \
attendees, topics, product, sentiment, materials, notes.

Return ONLY a JSON object of the form:
{ "changed_fields": { "<field_name>": <new_value>, ... } }

Where <new_value> matches the same type as in CURRENT_STATE (string, or array of strings). \
If nothing is actually being changed, return { "changed_fields": {} }.
Respond with raw JSON only.
"""


def run(user_message: str, current_interaction: Dict[str, Any]) -> Dict[str, Any]:
    prompt = (
        f"CURRENT_STATE:\n{json.dumps(current_interaction, indent=2)}\n\n"
        f"REP_MESSAGE:\n{user_message}"
    )
    result = call_json_llm(SYSTEM_PROMPT, prompt)
    changed = result.get("changed_fields", {}) or {}

    updated = dict(current_interaction)
    for key, value in changed.items():
        if key in updated:
            updated[key] = value

    updated["status"] = "draft"
    return updated, list(changed.keys())
