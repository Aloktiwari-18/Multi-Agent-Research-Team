"""Writer Agent — drafts a polished Markdown report from the research data."""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_anthropic import ChatAnthropic

from backend.agents.state import AgentState

SYSTEM_PROMPT = """\
You are the **Writer Agent** on a multi-agent research team.

Your responsibilities:
1. Take the Research Brief from the Researcher and any previous fact-check
   feedback.
2. Write a polished, well-structured **Markdown report** that answers the
   original user query comprehensively.

Rules:
- Use clear headings (##), bullet lists, and tables where appropriate.
- **Cite every factual claim** with an inline Markdown link to the source.
- Aim for ~800-1200 words.
- If the Fact-Checker flagged issues, address them specifically in this
  revision.
- Write in a professional, authoritative tone suitable for a whitepaper.
"""


def writer_node(state: AgentState, llm: ChatAnthropic) -> dict:
    """Draft (or revise) the research report."""
    revision_count = state.get("revision_count", 0)
    is_revision = revision_count > 0

    context_parts = [
        f"Original query: {state['query']}",
        f"Research Brief:\n{state['research_data']}",
    ]
    if is_revision:
        context_parts.append(
            f"Previous draft:\n{state.get('draft', '')}"
        )
        context_parts.append(
            f"Fact-Checker feedback:\n{state.get('fact_check_result', '')}"
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="\n\n---\n\n".join(context_parts)),
    ]

    response = llm.invoke(messages)

    action = "Revised" if is_revision else "Drafted"
    return {
        "draft": response.content,
        "agent_logs": [
            f"✍️ **Writer** — {action} the report (revision #{revision_count})."
        ],
        "messages": [response],
    }
