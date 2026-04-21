"""Writer Agent — drafts a polished Markdown report from the research data."""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from backend.agents.state import AgentState
SYSTEM_PROMPT = """\
You are the Writer Agent.

Create a structured, professional research report using the provided research and feedback.

## Instructions

- Write a clear and analytical report with:
  - key insights
  - comparisons
  - short reasoning
  - industry impact
  - advantages vs limitations
  - future trends (3–5 years)

## Structure

## Introduction  
## Key Technologies / Insights  
## Market & Comparison  
## Impact & Challenges  
## Future Outlook  
## Conclusion  

## Rules

- Keep content concise but meaningful  
- Avoid repetition and unnecessary detail  
- Use bullet points or tables where useful  
- Include sources where available  
- Improve based on feedback if provided  

## Goal

Produce a high-quality, insight-driven report within limited tokens.
"""


def _trim(text: str, limit: int) -> str:
    return (text or "")[:limit]

def writer_node(state: AgentState, llm) -> dict:
    revision_count = state.get("revision_count", 0)
    is_revision = revision_count > 0

    # 🔥 HARD BUDGET (safe for 6k TPM)
    research = _trim(state.get("research_data"), 1100)
    draft    = _trim(state.get("draft"), 600)
    feedback = _trim(state.get("fact_check_result"), 300)

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