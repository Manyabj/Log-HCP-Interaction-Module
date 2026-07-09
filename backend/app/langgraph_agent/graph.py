"""
LangGraph orchestration.

Flow:

    START
      |
      v
  classify_intent  (LLM decides: log | edit | clear | summarize | save | chat)
      |
      +--> log_node        --> LogInteractionTool
      +--> edit_node       --> EditInteractionTool
      +--> clear_node      --> ClearFieldTool
      +--> summarize_node  --> SummarizeInteractionTool
      +--> save_node       --> ValidateInteractionTool
      +--> chat_node       --> plain conversational reply
      |
      v
  compose_reply   (LLM turns the tool result into a natural reply)
      |
      v
     END
"""
from typing import Any, Dict

from langgraph.graph import StateGraph, END

from app.langgraph_agent.state import InteractionState, empty_interaction
from app.langgraph_agent.agents.extraction_agent import classify_intent
from app.langgraph_agent.tools import (
    log_interaction_tool,
    edit_interaction_tool,
    clear_field_tool,
    summarize_interaction_tool,
    validate_interaction_tool,
)
from app.langgraph_agent.llm import call_chat_llm

CHAT_SYSTEM_PROMPT = """You are an AI CRM assistant helping a pharmaceutical sales rep log \
a Healthcare Professional (HCP) interaction, similar to Veeva CRM's assistant. Be concise, \
professional, and friendly. You never ask the rep to use a form — the ONLY way data gets \
into the system is through this chat, and the structured form on screen updates automatically \
from what you extract. Keep replies to 1-3 sentences."""


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def node_classify(state: InteractionState) -> Dict[str, Any]:
    interaction = state.get("interaction") or empty_interaction()
    intent = classify_intent(state["user_message"], interaction)
    return {"intent": intent, "interaction": interaction}


def node_log(state: InteractionState) -> Dict[str, Any]:
    updated = log_interaction_tool.run(state["user_message"], state["interaction"])
    return {"interaction": updated, "tool_used": "LogInteractionTool"}


def node_edit(state: InteractionState) -> Dict[str, Any]:
    updated, changed = edit_interaction_tool.run(state["user_message"], state["interaction"])
    return {
        "interaction": updated,
        "tool_used": "EditInteractionTool",
        "extracted_fields": {f: updated.get(f) for f in changed},
    }


def node_clear(state: InteractionState) -> Dict[str, Any]:
    updated, cleared = clear_field_tool.run(state["user_message"], state["interaction"])
    return {
        "interaction": updated,
        "tool_used": "ClearFieldTool",
        "clear_targets": cleared,
    }


def node_summarize(state: InteractionState) -> Dict[str, Any]:
    summary = summarize_interaction_tool.run(state["interaction"])
    updated = dict(state["interaction"])
    updated["summary"] = summary
    return {"interaction": updated, "tool_used": "SummarizeInteractionTool", "reply": summary}


def node_save(state: InteractionState) -> Dict[str, Any]:
    is_valid, missing = validate_interaction_tool.run(state["interaction"])
    updated = dict(state["interaction"])
    if is_valid:
        updated["status"] = "validated"
    return {
        "interaction": updated,
        "tool_used": "ValidateInteractionTool",
        "is_valid_for_save": is_valid,
        "missing_fields": missing,
    }


def node_chat(state: InteractionState) -> Dict[str, Any]:
    history = state.get("conversation_history", [])
    reply = call_chat_llm(CHAT_SYSTEM_PROMPT, history + [{"role": "user", "content": state["user_message"]}])
    return {"tool_used": "ChatOnly", "reply": reply}


def node_compose_reply(state: InteractionState) -> Dict[str, Any]:
    # If a node already produced a final reply (summarize / chat), keep it.
    if state.get("reply"):
        return {"reply": state["reply"]}

    intent = state.get("intent")
    interaction = state["interaction"]

    if intent == "save":
        if state.get("is_valid_for_save"):
            reply = (
                "Everything looks complete. The interaction is validated and ready to save — "
                "click Save Interaction to submit it."
            )
        else:
            from app.langgraph_agent.tools.validate_interaction_tool import missing_field_labels
            labels = missing_field_labels(state.get("missing_fields", []))
            reply = (
                "Before I can save this, I still need a couple of details: "
                + "; ".join(f"please specify {label}" for label in labels) + "."
            )
        return {"reply": reply}

    if intent == "clear":
        targets = state.get("clear_targets", [])
        if targets:
            reply = f"Done — cleared: {', '.join(targets)}."
        else:
            reply = "I couldn't tell which field you wanted cleared — could you specify it?"
        return {"reply": reply}

    if intent == "edit":
        changed = list(state.get("extracted_fields", {}).keys())
        if changed:
            reply = f"Got it — updated: {', '.join(changed)}. Everything else stays the same."
        else:
            reply = "I didn't detect any actual changes from that — could you clarify what to update?"
        return {"reply": reply}

    # intent == "log" (default)
    filled = [k for k, v in interaction.items() if v not in (None, "", []) and k != "status"]
    reply = "Got it — I've updated the interaction form with: " + ", ".join(filled) + "."
    return {"reply": reply}


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def route_after_classify(state: InteractionState) -> str:
    return {
        "log": "log_node",
        "edit": "edit_node",
        "clear": "clear_node",
        "summarize": "summarize_node",
        "save": "save_node",
        "chat": "chat_node",
    }.get(state.get("intent", "log"), "log_node")


def build_graph():
    workflow = StateGraph(InteractionState)

    workflow.add_node("classify_intent", node_classify)
    workflow.add_node("log_node", node_log)
    workflow.add_node("edit_node", node_edit)
    workflow.add_node("clear_node", node_clear)
    workflow.add_node("summarize_node", node_summarize)
    workflow.add_node("save_node", node_save)
    workflow.add_node("chat_node", node_chat)
    workflow.add_node("compose_reply", node_compose_reply)

    workflow.set_entry_point("classify_intent")

    workflow.add_conditional_edges("classify_intent", route_after_classify, {
        "log_node": "log_node",
        "edit_node": "edit_node",
        "clear_node": "clear_node",
        "summarize_node": "summarize_node",
        "save_node": "save_node",
        "chat_node": "chat_node",
    })

    for node in ["log_node", "edit_node", "clear_node", "summarize_node", "save_node", "chat_node"]:
        workflow.add_edge(node, "compose_reply")

    workflow.add_edge("compose_reply", END)

    return workflow.compile()


# Compiled once at import time and reused across requests.
agent_graph = build_graph()
