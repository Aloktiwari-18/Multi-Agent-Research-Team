"""Researcher Agent — uses Tavily to find real-time sources and extract data."""

from __future__ import annotations

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from backend.agents.state import AgentState
SYSTEM_PROMPT = """\
You are the Researcher Agent.

Your goal is to gather HIGH-QUALITY, TRUSTED information.

## Instructions

- For each sub-question:
  - Select ONLY the most relevant 2 sources
  - Prefer strong sources (official, research, trusted media)
  - Avoid weak or duplicate sources

- Each point:
  - 1–2 lines maximum
  - Include key insight (not generic text)

## Output Format

## Research Brief

### <Sub-question>

- [Source Title](URL): Key insight (1–2 lines)
- [Source Title](URL): Key insight

### <Next sub-question>
- same format

## Rules

- Maximum 2 sources per question
- Focus on QUALITY over quantity
- Avoid repetition
- Keep output concise but meaningful

## Goal

Produce a strong, high-signal research brief that enables accurate report writing.
"""
import os

is_local = os.getenv("ENV") == "local"
MAX_SEARCH_RESULTS = 5 if is_local else 2


def _build_researcher_chain(llm: ChatGroq, tavily_api_key: str):
    """Create an LLM chain with the Tavily search tool bound."""
    search_tool = TavilySearchResults(
        max_results=MAX_SEARCH_RESULTS,
        tavily_api_key=tavily_api_key,
    )
    return llm.bind_tools([search_tool]), search_tool


def researcher_node(state: AgentState, llm: ChatGroq, tavily_api_key: str) -> dict:
    """Search the web for sources relevant to the research plan."""
    llm_with_tools, search_tool = _build_researcher_chain(llm, tavily_api_key)

    # Step 1 — ask the LLM to decide what to search
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Research Plan:\n{state['research_plan']}\n\n"
                "Use the search tool to investigate each sub-question, then "
                "compile a Research Brief with citations."
            )
        ),
    ]

    response = llm_with_tools.invoke(messages)

    # Step 2 — execute any tool calls the model requested
    all_results: list[str] = []
    if response.tool_calls:
        for tool_call in response.tool_calls:
            query = tool_call["args"].get("query", state["query"])
            results = search_tool.invoke({"query": query})
            formatted = "\n".join(
                f"- [{r.get('title', 'Source')}]({r.get('url', '')}): {r.get('content', '')[:250]}"
                for r in results
                if isinstance(r, dict)
            )
            all_results.append(f"### Search: {query}\n{formatted}")

    # Step 3 — have the LLM synthesise the raw results into a brief
    raw_data = "\n\n".join(all_results) if all_results else "No search results found."
    synthesis_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Research Plan:\n{state['research_plan']}\n\n"
                f"Raw search results:\n{raw_data}\n\n"
                "Now compile a structured Research Brief with citations."
            )
        ),
    ]
    synthesis = llm.invoke(synthesis_messages)

    return {
        "research_data": synthesis.content,
        "agent_logs": [
            f"🕵️ **Researcher** — Searched {len(all_results)} sub-topics and compiled a Research Brief."
        ],
        "messages": [synthesis],
    }
