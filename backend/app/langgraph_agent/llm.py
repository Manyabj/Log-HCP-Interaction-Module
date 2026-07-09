"""
Thin wrapper around the Groq API.

Two model roles are used, both configurable via environment variables:

- `reasoning` model (default: llama-3.3-70b-versatile) is used for structured
  entity extraction / intent classification, where strict JSON output and
  stronger reasoning matter.
- `chat` model (default: gemma2-9b-it) is used for generating natural
  language replies to the user (summaries, follow-up questions, confirmations).

No extraction logic is hardcoded in Python — every NLP task (entity
extraction, sentiment detection, summarization, follow-up question
generation) is delegated to the LLM via prompts defined below.
"""
import json
from typing import Any, Dict, List, Optional

from groq import Groq

from app.config import settings

_client: Optional[Groq] = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def call_json_llm(system_prompt: str, user_prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Calls the Groq reasoning model and forces a JSON object response.
    Used for entity extraction / intent classification / diffing.
    """
    client = get_client()
    model_name = model or settings.groq_reasoning_model

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Groq Error:", repr(e))
        raise

    raw = completion.choices[0].message.content
    if isinstance(raw, dict):
        return raw

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Defensive fallback: extract the first {...} block if the model
        # wrapped the JSON in extra text despite json_object mode.
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start:end + 1])
        raise


def call_chat_llm(system_prompt: str, conversation: List[Dict[str, str]], model: Optional[str] = None) -> str:
    """
    Calls the Groq conversational model to produce a natural-language reply.
    `conversation` is a list of {"role": "user"|"assistant", "content": str}.
    """
    client = get_client()
    model_name = model or settings.groq_chat_model

    messages = [{"role": "system", "content": system_prompt}] + conversation

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.4,
    )
    return completion.choices[0].message.content.strip()
