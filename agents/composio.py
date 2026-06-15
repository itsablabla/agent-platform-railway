"""
Composio Agent
==============

Connects to the Composio Connect MCP gateway, exposing the user's
authenticated SaaS tools (Gmail, Slack, GitHub, Notion, etc.) as agent
tools. AgentOS handles the MCP connect/close lifecycle.

The Composio API key is read from COMPOSIO_API_KEY and sent on the
``x-consumer-api-key`` request header.
"""

from agno.agent import Agent

from app.settings import default_model
from db import assistant_knowledge, get_postgres_db
from agents.tools import ALL_MCP_TOOLS


COMPOSIO_INSTRUCTIONS = """\
You are the Composio Agent. You can act on the user's connected SaaS
accounts (Gmail, Slack, GitHub, Notion, Calendar, etc.) through Composio
Connect.

Before performing a destructive or irreversible action (send, delete,
modify, transfer), summarise what you are about to do and ask the user
to confirm. List the tools you used to answer the question.
"""


composio_agent = Agent(
    id="composio",
    name="Composio",
    model=default_model(),
        compress_tool_results=True,
    db=get_postgres_db(),
    tools=ALL_MCP_TOOLS,
    instructions=COMPOSIO_INSTRUCTIONS,
    knowledge=assistant_knowledge,
    search_knowledge=True,
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
