"""Supervisor Agent — receives the user query and produces a research plan."""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_anthropic import ChatAnthropic

from backend.agents.state import AgentState

SYSTEM_PROMPT = """\
You are the **Supervisor Agent** of a multi-agent research team.

Your responsibilities:
1. Receive the user's research query.
2. Break it down into 3-5 concrete research sub-questions that the Researcher
   should investigate.
3. Output a structured **Research Plan** in Markdown with numbered sub-questions.

Rules:
- Be specific. Each sub-question should be independently searchable.
- Include the scope and focus area for each sub-question.
- Do NOT perform research yourself — only create the plan.
"""


def supervisor_node(state: AgentState, llm: ChatAnthropic) -> dict:
    """Analyse the user query and produce a research plan."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Research query:\n\n{state['query']}"),
    ]

    response = llm.invoke(messages)
    plan = response.content

    return {
        "research_plan": plan,
        "agent_logs": [
            "🧑‍💼 **Supervisor** — Received query and created research plan."
        ],
        "messages": [response],
    }
