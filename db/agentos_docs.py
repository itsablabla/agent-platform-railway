"""
AgentOS API Documentation Knowledge Base
=========================================

Dedicated PgVector knowledge base for the AgentOS REST API docs.
Vectors land in ``agentos_api_kb``; raw content in ``agentos_api_kb_contents``.
Populated by running:  python scripts/load_agentos_docs.py
"""

from db.session import create_knowledge

agentos_docs_knowledge = create_knowledge(
    name="AgentOS API Documentation",
    table_name="agentos_api_kb",
)
