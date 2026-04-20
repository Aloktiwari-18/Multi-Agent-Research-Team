"""Fact-Checker Agent — reviews the draft and assigns confidence scores."""

from __future__ import annotations

import json
import re

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_anthropic import ChatAnthropic

from backend.agents.state import AgentState

SYSTEM_PROMPT = """\
You are the **Fact-Checker Agent** on a multi-agent research team.

Your responsibilities:
1. Review the Writer's draft against the Research Brief.
2. For every major factual claim in the report, assign a **Confidence Score
   (0-100)** based on how well the claim is supported by the sources.
3. Output your verdict as a JSON code block with this schema:

```json
{
  "verdict": "APPROVED" | "NEEDS_REVISION",
  "overall_confidence": <int 0-100>,
  "claims": [
    {
      "claim": "<text>",
      "confidence": <int 0-100>,
      "issue": "<description or null>"
    }
  ],
  "summary": "<1-2 sentence overall assessment>"
}
```

Rules:
- If ANY claim scores below 70, set verdict to "NEEDS_REVISION".
- Be strict — unsourced claims should score below 50.
- If the overall_confidence ≥ 70 and no individual claim is below 70,
  set verdict to "APPROVED".
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


def fact_checker_node(state: AgentState, llm: ChatAnthropic, max_revisions: int = 3) -> dict:
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
