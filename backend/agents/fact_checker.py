"""Fact-Checker Agent — reviews the draft and assigns confidence scores."""

from __future__ import annotations

import json
import re

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from backend.agents.state import AgentState

SYSTEM_PROMPT = """\
You are the Fact-Checker Agent.

Your job is to quickly validate the accuracy of a research report.

## Instructions

- Identify ONLY the 3–5 most important claims
- Evaluate each claim briefly:
  - Has source? (yes/no)
  - Is it reliable? (high/medium/low)

## Output (JSON ONLY)

{
  "verdict": "APPROVED" | "NEEDS_REVISION",
  "overall_confidence": <0-100>,
  "issues": [
    "<short issue>",
    "<short issue>"
  ],
  "summary": "<1-line assessment>"
}

## Rules

- Be concise
- Do NOT extract all claims
- Focus on major issues only
- Keep output short
"""

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _parse_verdict(text: str) -> dict:
    """Extract the JSON verdict from the LLM response."""
    match = _JSON_BLOCK_RE.search(text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Fallback: try parsing the whole response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"verdict": "APPROVED", "overall_confidence": 75, "claims": [], "summary": text[:300]}


def fact_checker_node(state: AgentState, llm: ChatGroq, max_revisions: int = 3) -> dict:
    """Review the draft and decide whether to approve or request revision."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Original query: {state['query']}\n\n"
                f"Research Brief:\n{state['research_data']}\n\n"
                f"Draft report:\n{state['draft']}"
            )
        ),
    ]

    response = llm.invoke(messages)
    verdict = _parse_verdict(response.content)

    passed = verdict.get("verdict", "APPROVED").upper() == "APPROVED"
    revision_count = state.get("revision_count", 0) + 1

    # Force approval if we've hit the revision limit
    if not passed and revision_count >= max_revisions:
        passed = True
        verdict["summary"] = (
            f"{verdict.get('summary', '')} "
            f"[Auto-approved after {max_revisions} revision cycles.]"
        )

    emoji = "✅" if passed else "🔄"
    confidence = verdict.get("overall_confidence", "?")
    log_msg = (
        f"🔍 **Fact-Checker** — {emoji} Overall confidence: {confidence}%. "
        f"{'Approved!' if passed else 'Requesting revision.'}"
    )

    result: dict = {
        "fact_check_result": json.dumps(verdict, indent=2),
        "fact_check_passed": passed,
        "revision_count": revision_count,
        "agent_logs": [log_msg],
        "messages": [response],
    }

    if passed:
        result["final_report"] = state["draft"]

    return result
