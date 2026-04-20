"""Supervisor Agent — receives the user query and produces a research plan."""

from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from backend.agents.state import AgentState

SYSTEM_PROMPT = """\
You are the Supervisor Agent.

Your job is to break the user query into 3–4 clear research questions.

## Instructions

- Each question must be:
  - specific
  - searchable
  - focused on a different aspect

## Cover these areas (if relevant):

- core concept
- technology / methods
- key players / market
- impact / applications
- challenges or future trends

## Output Format

## Research Plan

1. <question>
2. <question>
3. <question>
4. <question>

## Rules

- Keep questions SHORT
- No explanations
- No answers
- Avoid generic questions

## Goal

Create a compact plan that guides strong research without adding unnecessary tokens.
"""


def supervisor_node(state: AgentState, llm: ChatGroq) -> dict:
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
