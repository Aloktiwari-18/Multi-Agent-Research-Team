"""LangGraph workflow — wires agents into an executable state graph."""

from __future__ import annotations

from functools import partial

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from backend.agents.fact_checker import fact_checker_node
from backend.agents.researcher import researcher_node
from backend.agents.state import AgentState
from backend.agents.supervisor import supervisor_node
from backend.agents.writer import writer_node
from backend.config import Settings


# ── Routing logic ────────────────────────────────────────────

def _route_after_fact_check(state: AgentState) -> str:
    """Conditional edge: loop back to writer or finish."""
    if state.get("fact_check_passed"):
        return "end"
    return "writer"


# ── Graph builder ────────────────────────────────────────────

def build_graph(settings: Settings | None = None):
    """Construct and compile the multi-agent research graph.

    Parameters
    ----------
    settings : Settings, optional
        If *None*, defaults are loaded from env vars.

    Returns
    -------
    CompiledGraph
        Ready-to-invoke LangGraph compiled graph.
    """
    if settings is None:
        from backend.config import get_settings
        settings = get_settings()

    llm = ChatAnthropic(
        model=settings.llm_model,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3,
        max_tokens=4096,
    )

    # Bind settings into each node so the graph only needs `state`
    sup = partial(supervisor_node, llm=llm)
    res = partial(researcher_node, llm=llm, tavily_api_key=settings.tavily_api_key)
    wri = partial(writer_node, llm=llm)
    fac = partial(fact_checker_node, llm=llm, max_revisions=settings.max_revisions)

    # ── Build graph ──────────────────────────────────────────
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", sup)
    graph.add_node("researcher", res)
    graph.add_node("writer", wri)
    graph.add_node("fact_checker", fac)

    graph.set_entry_point("supervisor")

    graph.add_edge("supervisor", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "fact_checker")

    graph.add_conditional_edges(
        "fact_checker",
        _route_after_fact_check,
        {"writer": "writer", "end": END},
    )

    # ── Checkpointer (in-memory; swap for Redis in production) ──
    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)
