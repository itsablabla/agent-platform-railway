"""
GPT-5.5 Agent
=============

Demonstrates routing the gpt-5.5 model via the Garza gateway.
"""

from agno.agent import Agent

from app.settings import default_model
from db import assistant_knowledge, get_postgres_db
from agents.tools import ALL_MCP_TOOLS


gpt55_agent = Agent(
    id="gpt-55",
    name="GPT 5.5",
    model=default_model(),
        compress_tool_results=True,
    db=get_postgres_db(),
    instructions="""\
You are a helpful assistant powered by GPT-5.5. Be clear and concise.

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
