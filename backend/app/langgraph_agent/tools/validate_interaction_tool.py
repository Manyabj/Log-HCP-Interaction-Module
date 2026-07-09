"""
Tool 5 — ValidateInteractionTool

Before the interaction can be saved, verify all mandatory fields are
present. If something is missing, the graph will ask a natural-language
follow-up question (via the LLM) instead of allowing a save.
"""
from typing import Any, Dict, List, Tuple

MANDATORY_FIELDS = ["hcp_name", "interaction_date", "product", "sentiment"]

FIELD_LABELS = {
    "hcp_name": "the doctor's name",
    "interaction_date": "the date of the interaction",
    "product": "which product was discussed",
    "sentiment": "the doctor's sentiment",
}


def run(current_interaction: Dict[str, Any]) -> Tuple[bool, List[str]]:
    missing = [
        field for field in MANDATORY_FIELDS
        if not current_interaction.get(field)
    ]
    is_valid = len(missing) == 0
    return is_valid, missing


def missing_field_labels(missing: List[str]) -> List[str]:
    return [FIELD_LABELS.get(f, f) for f in missing]
