
"""
Tool 4 — SummarizeInteractionTool

Generates a concise, professional summary of the interaction captured
so far, using the conversational Groq model (gemma2-9b-it).
"""
import json
from typing import Any, Dict

from app.langgraph_agent.llm import call_chat_llm

SYSTEM_PROMPT = """You are an assistant that writes concise, professional call-report \
summaries for pharmaceutical sales reps, based on structured HCP interaction data. \
Write 2-4 sentences, factual, no bullet points, no headers. If a field is missing, \
simply omit it rather than mentioning that it's missing."""


def run(current_interaction: Dict[str, Any]) -> str:
    user_prompt = (
        "Write a short summary of this HCP interaction based on the following "
        f"structured data:\n{json.dumps(current_interaction, indent=2)}"
    )
    summary = call_chat_llm(SYSTEM_PROMPT, [{"role": "user", "content": user_prompt}])
    return summary