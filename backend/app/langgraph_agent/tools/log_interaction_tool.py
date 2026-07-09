"""
Tool 1 — LogInteractionTool

Used the first time (or any time) the user describes a brand-new
interaction in free text, e.g.:

  "Today I met Dr. Smith and discussed Product X. The doctor showed
   positive sentiment and I shared brochures."

The LLM extracts every field it can find and we merge it into the
current interaction dict. Fields the model could not find are left
untouched (so this can also be safely re-used mid-conversation to
add newly-mentioned details without wiping previously captured ones).
"""
from typing import Any, Dict

from app.langgraph_agent.llm import call_json_llm

SYSTEM_PROMPT = """You are a clinical CRM entity-extraction engine for a pharmaceutical \
sales rep's "Log HCP Interaction" tool (similar to Veeva CRM).

Extract structured data from the rep's free-text message about a meeting/call/event \
with a Healthcare Professional (HCP). Return ONLY a single JSON object with exactly \
these keys (use null or [] when information is not present in the message):

{
  "hcp_name": string|null,          // e.g. "Dr. Smith"
  "interaction_type": string|null,  // one of: "Meeting", "Call", "Email", "Event", "Visit"
  "interaction_date": string|null,  // keep the rep's own wording, e.g. "today", "2026-07-08", "yesterday"
  "interaction_time": string|null,  // e.g. "10:30 AM" if mentioned
  "attendees": string[],            // additional people present besides the HCP
  "topics": string[],               // discussion topics / subjects covered
  "product": string|null,           // the product discussed, e.g. "Product X"
  "sentiment": string|null,         // one of: "Positive", "Neutral", "Negative"
  "materials": string[],            // materials/samples shared, e.g. ["Brochure"]
  "notes": string|null              // any other free-form remark worth keeping
}

Rules:
- Do not invent information that is not implied by the message.
- Normalize sentiment words (e.g. "very happy", "receptive" -> "Positive"; "unhappy", "reluctant" -> "Negative").
- Respond with raw JSON only, no commentary, no markdown fences.
"""


def run(user_message: str, current_interaction: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts structured fields from `user_message` and merges them into
    `current_interaction`. Returns the updated interaction dict."""
    extracted = call_json_llm(SYSTEM_PROMPT, user_message)

    updated = dict(current_interaction)
    for key, value in extracted.items():
        if key not in updated:
            continue
        if value in (None, "", []):
            continue  # keep existing value, don't overwrite with empty data
        if isinstance(value, list):
            # merge lists uniquely instead of clobbering
            existing = updated.get(key) or []
            merged = list(dict.fromkeys([*existing, *value]))
            updated[key] = merged
        else:
            updated[key] = value

    updated["status"] = "draft"
    return updated
