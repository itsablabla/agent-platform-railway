"""
AdminOps Agent
==============

Demonstrates AgentOS approval flows. Any tool decorated with ``@approval``
pauses the run until an admin resolves the request from the AgentOS
Control Plane (or the /approvals API).
"""

from agno.agent import Agent
from agno.approval import approval
from agno.tools import tool

from app.settings import default_model
from db import assistant_knowledge, get_postgres_db


ADMIN_OPS_INSTRUCTIONS = """\
You are AdminOps. You help operators run privileged maintenance tasks.

When the user asks to delete a resource, call ``delete_resource``. The
request will pause for human approval — do not retry; wait for the
operator to approve or reject from the AgentOS Control Plane.
"""


@approval
@tool(requires_confirmation=True)
def delete_resource(resource_id: str) -> str:
    """Permanently delete a resource. Requires admin approval before running."""
    return f"Resource {resource_id} has been deleted."


admin_ops = Agent(
    id="admin-ops",
    name="AdminOps",
    model=default_model(),
    db=get_postgres_db(),
    tools=[delete_resource],
    instructions=ADMIN_OPS_INSTRUCTIONS,
    knowledge=assistant_knowledge,
    search_knowledge=True,
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
