"""
AgentOS Entrypoint
==================
"""

from contextlib import asynccontextmanager
from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.utils.log import log_info

from agents.admin_ops import admin_ops
from agents.e2b_coder import e2b_coder
from app.interfaces import Discord, Telegram
from agents.claude_opus import claude_opus_agent
from agents.code_search import code_search
from agents.composio import composio_agent
from agents.gpt_55 import gpt55_agent
from agents.jada import jada
from agents.kimi import kimi_agent
from agents.openrouter import openrouter_agent
from agents.web_search import web_search
from app.settings import build_openrouter_registry
from db import get_postgres_db

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
runtime_env = getenv("RUNTIME_ENV", "prd")
scheduler_base_url = getenv("AGENTOS_URL", "http://127.0.0.1:8000")

# ---------------------------------------------------------------------------
# Interfaces
# - The CodeSearch agent becomes available on Slack when both env vars are set
# ---------------------------------------------------------------------------
SLACK_BOT_TOKEN = getenv("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = getenv("SLACK_SIGNING_SECRET", "")

interfaces: list = []
if SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET:
    from agno.os.interfaces.slack import Slack

    interfaces.append(
        Slack(
            agent=code_search,
            streaming=True,
            token=SLACK_BOT_TOKEN,
            signing_secret=SLACK_SIGNING_SECRET,
            resolve_user_identity=True,
        )
    )

if getenv("TELEGRAM_BOT_TOKEN"):
    interfaces.append(Telegram(agent=jada))

if getenv("DISCORD_PUBLIC_KEY") and getenv("DISCORD_BOT_TOKEN"):
    interfaces.append(Discord(agent=jada))


# ---------------------------------------------------------------------------
# Lifespan — extension hook for app-level startup / teardown.
#
# AgentOS handles the MCP lifecycle (connect on startup, close on shutdown).
# Keep this hook in place so you can plug in your own setup as needed.
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app):  # type: ignore[no-untyped-def]
    log_info("AgentOS lifespan: startup")

    # Eagerly connect each MCP toolkit exactly once.
    # All agents share the same MCPTools object instances (defined in tools.py),
    # so we deduplicate by object id to avoid spawning duplicate stdio processes
    # or corrupting HTTP connection state — either of which causes
    # "Failed to initialize MCP toolkit" on every subsequent run.
    _connected: set[int] = set()
    all_agents = [web_search, code_search, admin_ops, composio_agent, jada,
                  claude_opus_agent, gpt55_agent, kimi_agent, openrouter_agent, e2b_coder]
    for agent in all_agents:
        for toolkit in getattr(agent, "tools", []):
            if toolkit is None or id(toolkit) in _connected:
                continue
            if hasattr(toolkit, "connect") and callable(toolkit.connect):
                _connected.add(id(toolkit))
                try:
                    await toolkit.connect()
                    log_info(f"MCP connected: {getattr(toolkit, 'name', toolkit.__class__.__name__)}")
                except Exception as exc:
                    log_info(f"MCP skipped: {getattr(toolkit, 'name', toolkit.__class__.__name__)} — {exc}")

    try:
        yield
    finally:
        log_info("AgentOS lifespan: shutdown")


# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------

# Pre-populate registry with all OpenRouter models so they appear in
# GET /registry?resource_type=model without needing one agent per model.
_registry = build_openrouter_registry()

agent_os = AgentOS(
    name="AgentOS",
    tracing=True,
    scheduler=True,
    scheduler_poll_interval=15,
    scheduler_base_url=scheduler_base_url,
    authorization=False,
    lifespan=lifespan,
    db=get_postgres_db(),
    registry=_registry,
    agents=[
        web_search,
        code_search,
        admin_ops,
        jada,
        composio_agent,
        claude_opus_agent,
        gpt55_agent,
        kimi_agent,
        openrouter_agent,
        e2b_coder,
    ],
    interfaces=interfaces,
    config=str(Path(__file__).parent / "config.yaml"),
)
app = agent_os.get_app()

# Mount custom interfaces that AgentOS doesn't manage natively
for _iface in interfaces:
    if hasattr(_iface, "get_router") and _iface.type in ("telegram", "discord"):
        app.include_router(_iface.get_router())


if __name__ == "__main__":
    agent_os.serve(app="app.main:app", reload=runtime_env == "dev")
