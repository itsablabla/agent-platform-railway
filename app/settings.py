"""
App Settings
============

Shared runtime objects for the platform.

All models route through the Garza LLM Gateway (OpenAI-compatible).
The gateway exposes a curated set of Claude, GPT, and Kimi models behind
one API at OPENAI_BASE_URL.

OpenRouter is also supported as a direct provider with access to all
public models via OPENROUTER_API_KEY.
"""

from os import getenv

from agno.models.openai import OpenAIChat
from agno.models.openai.like import OpenAILike

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
    "kimi-k2.6",
]

DEFAULT_GARZA_MODEL = "kimi-k2.6"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "anthropic/claude-sonnet-4-5"


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


def openrouter_model(model_id: str | None = None) -> OpenAILike:
    """Return an OpenRouter model instance.

    Defaults to DEFAULT_OPENROUTER_MODEL when no id is given.
    """
    chosen = model_id or getenv("OPENROUTER_MODEL") or DEFAULT_OPENROUTER_MODEL
    return OpenAILike(
        id=chosen,
        api_key=getenv("OPENROUTER_API_KEY"),
        base_url=OPENROUTER_BASE_URL,
    )


def build_openrouter_registry():
    """Build a Registry pre-populated with every available model.

    Includes:
    - All Garza LLM Gateway models (OpenAIChat via OPENAI_BASE_URL)
    - All public OpenRouter models (OpenAILike via openrouter.ai)

    The Registry is passed to AgentOS so models appear in
    GET /registry?resource_type=model and in the Studio model picker.
    """
    import json
    import urllib.request

    from agno.registry import Registry
    from agno.utils.log import log_info, log_warning

    all_models: list = []

    # Garza LLM Gateway models
    for model_id in GARZA_MODELS:
        all_models.append(default_model(model_id))
    log_info(f"Registry: added {len(GARZA_MODELS)} Garza gateway models")

    # OpenRouter models
    api_key = getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        log_warning("OPENROUTER_API_KEY not set — skipping OpenRouter model discovery")
    else:
        try:
            req = urllib.request.Request(
                f"{OPENROUTER_BASE_URL}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            or_models = data.get("data", [])
            for m in or_models:
                all_models.append(openrouter_model(m["id"]))
            log_info(f"Registry: added {len(or_models)} OpenRouter models")
        except Exception as exc:
            log_warning(f"OpenRouter model discovery failed: {exc}")

    registry = Registry(models=all_models)
    log_info(f"Registry: {len(all_models)} total models registered")
    return registry
