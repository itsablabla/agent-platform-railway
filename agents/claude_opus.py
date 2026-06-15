"""
Claude Opus 4.8 Agent
=====================

Demonstrates routing a specific Garza model via ``default_model(model_id=...)``.
"""

from agno.agent import Agent

from app.settings import default_model
from db import assistant_knowledge, get_postgres_db
from agents.tools import ALL_MCP_TOOLS


claude_opus_agent = Agent(
    id="claude-opus",
    name="Claude Opus",
    model=default_model(),
    db=get_postgres_db(),
    instructions="""\
You are a helpful assistant powered by Claude Opus 4.8. Be clear and concise.

    You can also access Composio tools for SaaS integrations, E2B for
code execution, and 1Password for secret management.
""",
    knowledge=assistant_knowledge,
    search_knowledge=True,
    tools=ALL_MCP_TOOLS,
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
