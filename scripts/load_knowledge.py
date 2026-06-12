#!/usr/bin/env python3
"""
Populate Assistant Knowledge Base
===================================

Loads Agno documentation and project context into the shared PgVector
knowledge base so agents can answer questions about the platform.

Usage:
    # Local (needs DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_DATABASE in env)
    python scripts/load_knowledge.py

    # Or connect to Railway DB via proxy:
    DATABASE_URL=postgresql+psycopg://... python scripts/load_knowledge.py
"""

from os import getenv

from db import assistant_knowledge


def main() -> None:
    print("Loading knowledge into Assistant Knowledge base...")
    print(f"DB URL: {getenv('DB_HOST', 'localhost')}:{getenv('DB_PORT', '5432')}")
    print()

    # Agno framework documentation
    print("1. Loading Agno docs...")
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

    print()
    print("Knowledge base populated successfully!")
    print("Agents can now use search_knowledge=True to reference this content.")


if __name__ == "__main__":
    main()
