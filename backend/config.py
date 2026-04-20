"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable settings pulled from env vars with sensible defaults."""

    # ── Required ──────────────────────────────────────────────
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))

    # ── Optional ──────────────────────────────────────────────
    langchain_api_key: str = field(default_factory=lambda: os.getenv("LANGCHAIN_API_KEY", ""))
    langchain_tracing: str = field(default_factory=lambda: os.getenv("LANGCHAIN_TRACING_V2", "false"))
    langchain_project: str = field(default_factory=lambda: os.getenv("LANGCHAIN_PROJECT", "multi-agent-research"))

    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"))

    # ── Constraints ───────────────────────────────────────────
    max_revisions: int = 3

    def apply_langsmith_env(self) -> None:
        """Push LangSmith env vars so the SDK picks them up."""
        if self.langchain_api_key:
            os.environ["LANGCHAIN_API_KEY"] = self.langchain_api_key
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = self.langchain_project


def get_settings(**overrides: str) -> Settings:
    """Build a Settings instance, allowing runtime overrides (e.g. from the
    Streamlit sidebar)."""
    env_defaults = Settings()
    merged = {
        "groq_api_key": overrides.get("groq_api_key") or env_defaults.groq_api_key,
        "tavily_api_key": overrides.get("tavily_api_key") or env_defaults.tavily_api_key,
        "langchain_api_key": overrides.get("langchain_api_key") or env_defaults.langchain_api_key,
        "redis_url": overrides.get("redis_url") or env_defaults.redis_url,
        "llm_model": overrides.get("llm_model") or env_defaults.llm_model,
    }
    settings = Settings(**merged)
    settings.apply_langsmith_env()
    return settings
