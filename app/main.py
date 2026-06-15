"""
AgentOS Entrypoint
==================
"""

from contextlib import asynccontextmanager
from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.utils.log import log_info
from sqlalchemy import text

from agents.admin_ops import admin_ops
from agents.e2b_coder import e2b_coder
from agents.log_analyst import log_analyst
from agents.railway_agent import railway_agent
from agents.security_agent import security_agent
from agents.session_analyst import session_analyst
from agents.system_operator import system_operator
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
from db.url import db_url
from teams.bug_testing import bug_testing_team

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

if getenv("TELEGRAM_BOT_TOKEN") or getenv("TELEGRAM_TOKEN"):
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

    # ── One-shot migration: fix debug team model ──────────────────────────
    # The debug team was created in Agno Studio with amazon/nova-pro-v1.
    # Switch it to moonshotai/kimi-k2.6 so the user’s runs actually work.
    try:
        import json
        from sqlalchemy import create_engine, inspect as sa_inspect
        engine = create_engine(db_url)
        inspector = sa_inspect(engine)
        all_tables = inspector.get_table_names()
        log_info(f"[migration] all tables: {all_tables}")
        team_tables = [t for t in all_tables if "team" in t.lower()]
        log_info(f"[migration] team-related tables: {team_tables}")
        candidates = ["agno_teams", "agno_team", "teams", "team", "os_teams"] + team_tables
        found = False
        for candidate in candidates:
            if candidate not in all_tables:
                continue
            with engine.connect() as conn:
                row = conn.execute(
                    text(f"SELECT id, model_data FROM {candidate} WHERE id = 'debug'")
                ).fetchone()
                if not row:
                    continue
                team_id, model_data = row
                md = json.loads(model_data) if isinstance(model_data, str) else (dict(model_data) if model_data else {})
                if md.get("id") == "moonshotai/kimi-k2.6":
                    log_info(f"[migration] debug team already on kimi-k2.6 (table={candidate})")
                    found = True
                    break
                md["id"] = "moonshotai/kimi-k2.6"
                md["name"] = "OpenAILike"
                md["provider"] = "OpenAI"
                conn.execute(
                    text(f"UPDATE {candidate} SET model_data = :md WHERE id = :tid"),
                    {"md": json.dumps(md), "tid": team_id},
                )
                conn.commit()
                log_info(f"[migration] debug team model switched to moonshotai/kimi-k2.6 (table={candidate})")
                found = True
                break
        if not found:
            log_info("[migration] debug team not found in any table")
    except Exception as exc:
        log_info(f"[migration] debug team model migration skipped: {exc}")

    # Eagerly connect each MCP toolkit exactly once.
    # All agents share the same MCPTools object instances (defined in tools.py),
    # so we deduplicate by object id to avoid spawning duplicate stdio processes
    # or corrupting HTTP connection state — either of which causes
    # "Failed to initialize MCP toolkit" on every subsequent run.
    _connected: set[int] = set()
    all_agents = [
        web_search, code_search, admin_ops, composio_agent, jada,
        claude_opus_agent, gpt55_agent, kimi_agent, openrouter_agent, e2b_coder,
        system_operator, railway_agent, security_agent, session_analyst, log_analyst,
    ]
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

    # Auto-register Telegram webhook now that the server is up.
    # Uses AGENTOS_URL (the public Railway domain) as the base.
    public_url = getenv("AGENTOS_URL", "").rstrip("/")
    if public_url:
        for iface in interfaces:
            if hasattr(iface, "register_webhook") and getattr(iface, "type", "") == "telegram":
                try:
                    result = await iface.register_webhook(f"{public_url}/telegram/webhook")
                    log_info(f"Telegram webhook registered: {result}")
                except Exception as exc:
                    log_info(f"Telegram webhook registration failed: {exc}")

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
    a2a_interface=True,
    lifespan=lifespan,
    db=get_postgres_db(),
    registry=_registry,
    agents=[
        # Operator hierarchy (top to bottom)
        system_operator,
        railway_agent,
        security_agent,
        session_analyst,
        log_analyst,
        # General-purpose agents
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
    teams=[
        bug_testing_team,
    ],
    interfaces=interfaces,
    config=str(Path(__file__).parent / "config.yaml"),
)
app = agent_os.get_app()



if __name__ == "__main__":
    agent_os.serve(app="app.main:app", reload=runtime_env == "dev")
