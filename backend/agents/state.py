"""Shared state schema that flows through every node in the agent graph."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


def _merge_logs(left: list[str], right: list[str]) -> list[str]:
    """Reducer: append new log entries to the existing list."""
    return (left or []) + (right or [])


class AgentState(TypedDict):
    """Typed state dictionary shared across all agent nodes.

    Attributes
    ----------
    query : str
        The original research question from the user.
    research_plan : str
        High-level plan produced by the Supervisor.
    research_data : str
        Sources and snippets collected by the Researcher.
    draft : str
        Current report draft produced by the Writer.
    fact_check_result : str
        Verdict and per-claim confidence scores from the Fact-Checker.
    fact_check_passed : bool
        Whether the draft passed fact-checking.
    revision_count : int
        Number of Writer ↔ Fact-Checker revision loops completed.
    agent_logs : list[str]
        Chronological status messages emitted to the frontend.
    final_report : str
        The approved, final Markdown report.
    messages : list
        LangGraph message accumulator (used internally by chat models).
    """

    query: str
    research_plan: str
    research_data: str
    draft: str
    fact_check_result: str
    fact_check_passed: bool
    revision_count: int
    agent_logs: Annotated[list[str], _merge_logs]
    final_report: str
    messages: Annotated[list, add_messages]
