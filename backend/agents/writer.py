"""Writer Agent — drafts a polished Markdown report from the research data."""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from backend.agents.state import AgentState
SYSTEM_PROMPT = """\
You are the Writer Agent.

Your task is to create a clear, structured, and insightful research report.

## Instructions

- Use the provided research data only
- Keep the report concise but meaningful
- Focus on key insights, not long explanations

## Output Structure

## Introduction
- Brief overview

## Key Insights
- Important findings (bullet points)

## Analysis
- Short reasoning and comparisons

## Conclusion
- Key takeaway

## Rules

- Keep total length MEDIUM (not too long)
- Avoid unnecessary detail
- Avoid repetition
- Include sources where available
- Do not expand beyond given data

## Goal

Produce a high-quality report within limited tokens while maintaining clarity and insight.
"""

def _trim(text: str, limit: int) -> str:
    return (text or "")[:limit]

def writer_node(state: AgentState, llm) -> dict:
    revision_count = state.get("revision_count", 0)
    is_revision = revision_count > 0

    # 🔥 HARD BUDGET (safe for 6k TPM)
    research = _trim(state.get("research_data"), 1000)
    draft    = _trim(state.get("draft"), 600)
    feedback = _trim(state.get("fact_check_result"), 350)

    context_parts = [
        f"Query:\n{_trim(state['query'], 300)}",
        f"Research Brief:\n{research}",
    ]

    if is_revision:
        context_parts.append(f"Previous Draft:\n{draft}")
        context_parts.append(f"Fact Feedback:\n{feedback}")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="\n\n".join(context_parts)),
    ]

    resp = llm.invoke(messages)

    return {
        "draft": resp.content,
        "agent_logs": [f"✍️ Writer — {'Revised' if is_revision else 'Drafted'}"],
        "messages": [resp],
    }