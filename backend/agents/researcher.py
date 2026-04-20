"""Researcher Agent — uses Tavily to find real-time sources and extract data."""

from __future__ import annotations

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from backend.agents.state import AgentState
SYSTEM_PROMPT = """\
You are the **Researcher Agent** on a multi-agent research team.

Your role is to act as a **professional research analyst** who gathers
high-quality, verifiable information from the web.

---

## 🎯 Your Responsibilities

1. Take the Research Plan from the Supervisor.
2. For EACH sub-question:
   - Use the Tavily web-search tool
   - Find **credible, recent, and relevant sources**
3. Compile findings into a structured **Research Brief (Markdown)**

---

## 🔍 Research Quality Rules (VERY IMPORTANT)

For EACH sub-question:

- Include **at least 2–3 real source URLs**
- Prefer:
  - official websites
  - research reports
  - trusted media (e.g., Bloomberg, Reuters, TechCrunch)
- Avoid:
  - generic summaries without sources
  - unverified claims

---

## 🧾 Citation Rules (STRICT)

- EVERY fact MUST have a source
- Use format:
  [Title](URL): short summary

Example:
- [OpenAI funding news](https://...): OpenAI raised...

- DO NOT write any claim without a source
- If no reliable source found → explicitly say:
  "No credible source found for this point"

---

## 🧠 Output Structure (MANDATORY)

## Research Brief

### 1. <Sub-question title>

- [Source Title](URL): Key finding (1–2 lines)
- [Source Title](URL): Key finding
- [Source Title](URL): Key finding

### 2. <Sub-question title>

- same structure...

---

## ⚠️ Critical Rules

- DO NOT write a final report
- DO NOT summarize everything into paragraphs
- DO NOT add opinions or conclusions
- ONLY provide **raw, source-backed findings**

---

## 🚀 Goal

Produce a **high-quality research brief with strong factual grounding**
so that the Writer Agent can generate an **accurate and insightful report**.
"""
import os

is_local = os.getenv("ENV") == "local"
MAX_SEARCH_RESULTS = 5 if is_local else 3


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
