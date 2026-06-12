"""
App Settings
============

Shared runtime objects for the platform.

All models route through the Garza LLM Gateway (OpenAI-compatible).
The gateway exposes a curated set of Claude, GPT, and Kimi models behind
one API at OPENAI_BASE_URL.
"""

from os import getenv

from agno.models.openai import OpenAIChat

# All 22 models available on the Garza LLM Gateway.
GARZA_MODELS: list[str] = [
    "claude-3-5-haiku-20241022",
    "claude-3-7-sonnet-20250219",
    "claude-fable-5",
    "claude-haiku-4-5-20251001",
    "claude-opus-4-1-20250805",
    "claude-opus-4-20250514",
    "claude-opus-4-5-20251101",
    "claude-opus-4-6",
    "claude-opus-4-7",
    "claude-opus-4-8",
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-6",
    "codex-auto-review",
    "garzaauto",
    "gpt-5.3-codex-spark",
    "gpt-5.4-mini",
    "gpt-5.5",
    "gpt-image-2",
    "kimi-k2",
    "kimi-k2-thinking",
    "kimi-k2.5",
]

DEFAULT_GARZA_MODEL = "claude-sonnet-4-5-20250929"


def default_model(model_id: str | None = None) -> OpenAIChat:
    """Return a fresh model instance per agent — avoids shared-state footguns.

    Resolution order for the model id:
      1. Explicit ``model_id`` arg
      2. ``GARZA_MODEL`` env var
      3. ``DEFAULT_GARZA_MODEL`` constant
    """
    chosen = model_id or getenv("GARZA_MODEL") or DEFAULT_GARZA_MODEL
    return OpenAIChat(
        id=chosen,
        api_key=getenv("OPENAI_API_KEY"),
        base_url=getenv("OPENAI_BASE_URL"),
    )
