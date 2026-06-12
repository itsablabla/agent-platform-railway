"""
Shared Knowledge Base
=====================

PgVector-backed knowledge surface shared by all agents. Documents land in
``assistant_kb`` (vectors) and ``assistant_kb_contents`` (raw content).
"""

from db.session import create_knowledge

assistant_knowledge = create_knowledge(
    name="Assistant Knowledge",
    table_name="assistant_kb",
)
