"""
OpenRouter Agent
================

Generic agent that routes requests through OpenRouter, giving access
to every model available on the platform (Llama, Gemini, DeepSeek,
Grok, Mistral, Qwen, and more).

The model defaults to DEFAULT_OPENROUTER_MODEL but can be overridden
at runtime via the OPENROUTER_MODEL env var or by passing model_id to
openrouter_model() when constructing a custom agent.
"""

from agno.agent import Agent

from app.settings import openrouter_model
from db import assistant_knowledge, get_postgres_db
from agents.tools import ALL_MCP_TOOLS


openrouter_agent = Agent(
    id="openrouter",
    name="OpenRouter",
    model=openrouter_model(),
    db=get_postgres_db(),
    instructions="""\
You are a helpful assistant powered by OpenRouter, which gives you access
to hundreds of frontier models including Llama, Gemini, DeepSeek, Grok,
Mistral, Qwen, and more.

Be clear, concise, and accurate. You have access to web search, Composio
SaaS integrations, E2B code execution sandboxes, and 1Password for
secret management.
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
