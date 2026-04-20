"""FastAPI backend — SSE streaming endpoint for the multi-agent research graph."""

from __future__ import annotations

import json
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.config import get_settings
from backend.demo import demo_sse_stream
from backend.graph.workflow import build_graph

# ── App ──────────────────────────────────────────────────────

app = FastAPI(
    title="Multi-Agent AI Research Team",
    version="1.0.0",
    description="Orchestrates Supervisor → Researcher → Writer → Fact-Checker agents via LangGraph.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ───────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str
    anthropic_api_key: str | None = None
    tavily_api_key: str | None = None
    langchain_api_key: str | None = None
    llm_model: str | None = None
    demo_mode: bool = False


# ── Helpers ──────────────────────────────────────────────────

def _sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _run_graph_sse(request: ResearchRequest) -> AsyncGenerator[str, None]:
    """Execute the graph and yield SSE events for each agent step."""
    overrides = {}
    if request.anthropic_api_key:
        overrides["anthropic_api_key"] = request.anthropic_api_key
    if request.tavily_api_key:
        overrides["tavily_api_key"] = request.tavily_api_key
    if request.langchain_api_key:
        overrides["langchain_api_key"] = request.langchain_api_key
    if request.llm_model:
        overrides["llm_model"] = request.llm_model

    settings = get_settings(**overrides)
    graph = build_graph(settings)

    initial_state = {
        "query": request.query,
        "research_plan": "",
        "research_data": "",
        "draft": "",
        "fact_check_result": "",
        "fact_check_passed": False,
        "revision_count": 0,
        "agent_logs": [],
        "final_report": "",
        "messages": [],
    }

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    yield _sse_event("status", {"message": "🚀 Starting multi-agent research pipeline..."})

    prev_logs_len = 0
    try:
        for step_output in graph.stream(initial_state, config=config):
            # step_output is {node_name: state_update}
            for node_name, state_update in step_output.items():
                # Emit new log entries
                new_logs = (state_update.get("agent_logs") or [])[:]
                for log in new_logs:
                    yield _sse_event("agent_log", {"agent": node_name, "message": log})

                # If final report is available, emit it
                if state_update.get("final_report"):
                    yield _sse_event("final_report", {"report": state_update["final_report"]})

        yield _sse_event("done", {"message": "✅ Research pipeline complete."})

    except Exception as e:
        yield _sse_event("error", {"message": f"❌ Pipeline error: {str(e)}"})


# ── Routes ───────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok"}


@app.post("/api/research")
async def research(request: ResearchRequest):
    """Run the multi-agent research pipeline, streaming results as SSE.
    Falls back to demo mode if demo_mode is set or no API keys are provided."""
    use_demo = request.demo_mode or (not request.anthropic_api_key and not request.tavily_api_key)
    stream = demo_sse_stream(request.query) if use_demo else _run_graph_sse(request)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
