"""
GPT-5.5 Agent
=============

Demonstrates routing the gpt-5.5 model via the Garza gateway.
"""

from agno.agent import Agent

from app.settings import default_model
from db import assistant_knowledge, get_postgres_db
from agents.tools import composio_tools, web_tools


gpt55_agent = Agent(
    id="gpt-55",
    name="GPT 5.5",
    model=default_model(model_id="gpt-5.5"),
    db=get_postgres_db(),
    instructions="""\
You are a helpful assistant powered by GPT-5.5. Be clear and concise.

You also have access to Composio tools for interacting with connected
SaaS accounts (Gmail, Slack, GitHub, Notion, etc.). Use these when the
user asks you to perform actions on their connected services.
""",
    knowledge=assistant_knowledge,
    search_knowledge=True,
    tools=[web_tools, composio_tools],
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
