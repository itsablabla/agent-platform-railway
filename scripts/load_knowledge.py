#!/usr/bin/env python3
"""
Populate Knowledge Bases
=========================

Loads documentation into two PgVector knowledge bases:

1. assistant_kb — general Agno framework docs (all agents)
2. agentos_api_kb — AgentOS API + A2A + operational docs (specialist agents)

Usage:
    # Local (needs DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_DATABASE in env)
    python scripts/load_knowledge.py

    # Or connect to Railway DB via proxy:
    DATABASE_URL=postgresql+psycopg://... python scripts/load_knowledge.py

    # Load only one KB:
    python scripts/load_knowledge.py --kb assistant
    python scripts/load_knowledge.py --kb agentos
"""

import sys
from os import getenv

from db import agentos_docs_knowledge, assistant_knowledge


def load_assistant() -> None:
    print("Loading → assistant_kb (general Agno framework docs)...")
    assistant_knowledge.load(
        urls=[
            "https://docs.agno.com/llms.txt",
            "https://docs.agno.com/introduction",
            "https://docs.agno.com/agent-os/introduction",
            "https://docs.agno.com/agent-os/scheduler",
            "https://docs.agno.com/evals/agent-as-judge",
            "https://docs.agno.com/teams/overview",
            "https://docs.agno.com/workflows/overview",
            "https://docs.agno.com/models/openai",
            "https://docs.agno.com/tools/toolkits",
            "https://docs.agno.com/agent-os/interfaces/overview",
        ],
        follow_redirects=True,
    )
    print("   Done.")


def load_agentos_docs() -> None:
    print("Loading → agentos_api_kb (AgentOS API + A2A + operational docs)...")
    agentos_docs_knowledge.load(
        urls=[
            # Core AgentOS
            "https://docs.agno.com/agent-os/introduction",
            "https://docs.agno.com/reference/agent-os/agent-os",
            # A2A inter-agent communication
            "https://docs.agno.com/agent-os/interfaces/a2a/introduction",
            "https://docs.agno.com/agent-os/client/a2a-client",
            "https://docs.agno.com/deploy/interfaces/a2a/overview",
            # Sessions, runs, traces
            "https://docs.agno.com/agent-os/sessions",
            "https://docs.agno.com/agent-os/runs",
            # Memory and knowledge
            "https://docs.agno.com/agent-os/memory",
            "https://docs.agno.com/agent-os/knowledge",
            # Scheduler and approvals
            "https://docs.agno.com/agent-os/scheduler",
            "https://docs.agno.com/agent-os/approvals",
            # Interfaces
            "https://docs.agno.com/agent-os/interfaces/overview",
            "https://docs.agno.com/agent-os/interfaces/telegram",
            "https://docs.agno.com/agent-os/interfaces/discord",
            "https://docs.agno.com/agent-os/interfaces/slack",
            # MCP and tools
            "https://docs.agno.com/tools/mcp",
            "https://docs.agno.com/tools/toolkits",
            # Agents and teams
            "https://docs.agno.com/agents/introduction",
            "https://docs.agno.com/teams/overview",
            "https://docs.agno.com/workflows/overview",
            # Deployment
            "https://docs.agno.com/deploy/introduction",
            "https://docs.agno.com/deploy/railway",
        ],
        follow_redirects=True,
    )
    print("   Done.")


def main() -> None:
    target = None
    for arg in sys.argv[1:]:
        if arg.startswith("--kb="):
            target = arg.split("=", 1)[1]
        elif arg == "--kb" and sys.argv.index(arg) + 1 < len(sys.argv):
            target = sys.argv[sys.argv.index(arg) + 1]

    print(f"DB: {getenv('DB_HOST', 'localhost')}:{getenv('DB_PORT', '5432')}")
    print()

    if target == "assistant":
        load_assistant()
    elif target == "agentos":
        load_agentos_docs()
    else:
        load_assistant()
        print()
        load_agentos_docs()

    print()
    print("Knowledge bases populated successfully.")
    print("Agents with search_knowledge=True can now reference this content.")


if __name__ == "__main__":
    main()
