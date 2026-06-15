"""
Jada Agent
==========

The main assistant — a general-purpose agent with access to web search,
codebase search, admin operations, and Composio-connected SaaS tools.
"""

from agno.agent import Agent

from agents.admin_ops import delete_resource
from agents.code_search import codebase_context
from agents.tools import ALL_MCP_TOOLS
from app.settings import default_model
from db import assistant_knowledge, get_postgres_db


JADA_INSTRUCTIONS = """\
you are main agenta

You have access to the following tools:
- **Web search** — search and fetch current information from the internet
- **Codebase search** — search and read files in your own codebase
- **Admin operations** — run privileged tasks (requires approval for destructive actions)
- **Composio** — interact with connected SaaS accounts (Gmail, Slack, GitHub, Notion, Calendar, etc.)

Use the right tool for the user's request. When using Composio tools for
destructive actions (send, delete, modify), ask the user to confirm first.
"""


jada = Agent(
    id="jada",
    name="Jada",
    model=default_model(),
    db=get_postgres_db(),
    tools=[
        *codebase_context.get_tools(),
        delete_resource,
        *ALL_MCP_TOOLS,
    ],
    instructions=JADA_INSTRUCTIONS,
    knowledge=assistant_knowledge,
    search_knowledge=True,
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
