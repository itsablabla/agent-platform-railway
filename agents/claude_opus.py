"""
Claude Opus 4.8 Agent
=====================

Demonstrates routing a specific Garza model via ``default_model(model_id=...)``.
"""

from agno.agent import Agent

from app.settings import default_model
from db import assistant_knowledge, get_postgres_db
from agents.composio import composio_tools


claude_opus_agent = Agent(
    id="claude-opus",
    name="Claude Opus",
    model=default_model(model_id="claude-opus-4-8"),
    db=get_postgres_db(),
    instructions="""\
You are a helpful assistant powered by Claude Opus 4.8. Be clear and concise.

You also have access to Composio tools for interacting with connected
SaaS accounts (Gmail, Slack, GitHub, Notion, etc.). Use these when the
user asks you to perform actions on their connected services.
""",
    knowledge=assistant_knowledge,
    search_knowledge=True,
    tools=[composio_tools],
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
