"""
AdminOps Agent
==============

System agent with full AgentOS API access plus approval flows.
Any tool decorated with ``@approval`` pauses the run until an admin
resolves the request from the AgentOS Control Plane (or the /approvals API).
"""

from agno.agent import Agent
from agno.approval import approval
from agno.tools import tool

from app.settings import openrouter_model
from db import assistant_knowledge, get_postgres_db
from agents.agentos_api import AGENTOS_API_TOOLS


@approval
@tool(requires_confirmation=True)
def delete_resource(resource_id: str) -> str:
    """Permanently delete a resource. Requires admin approval before running."""
    return f"Resource {resource_id} has been deleted."


admin_ops = Agent(
    id="agno-it-admin",
    name="Agno IT Admin",
    model=openrouter_model("moonshotai/kimi-k2.6"),
    db=get_postgres_db(),
    tools=[delete_resource, *AGENTOS_API_TOOLS],
    instructions="""\
You are AdminOps — the system agent with full access to every AgentOS REST API endpoint.

## AgentOS API Tools
You have ~100 tools prefixed with `api_` that map 1:1 to AgentOS REST endpoints:

**Agents & Runs**: api_list_agents, api_get_agent, api_create_agent_run, api_list_agent_runs,
api_get_agent_run, api_continue_agent_run, api_cancel_agent_run

**Teams**: api_list_teams, api_get_team, api_create_team_run, api_list_team_runs,
api_get_team_run, api_cancel_team_run

**Workflows**: api_list_workflows, api_get_workflow, api_execute_workflow,
api_get_workflow_run, api_cancel_workflow_run

**Sessions**: api_list_sessions, api_create_session, api_get_session, api_update_session,
api_rename_session, api_delete_session, api_delete_multiple_sessions, api_get_session_runs

**Memory**: api_list_memories, api_create_memory, api_update_memory, api_delete_memory,
api_get_memory_topics, api_get_user_memory_statistics, api_optimize_user_memories

**Knowledge**: api_list_knowledge_content, api_upload_knowledge_content,
api_upload_remote_knowledge_content, api_search_knowledge, api_delete_all_knowledge_content

**Schedules**: api_list_schedules, api_create_schedule, api_update_schedule,
api_delete_schedule, api_enable_schedule, api_disable_schedule, api_trigger_schedule

**Approvals**: api_list_approvals, api_get_approval_count, api_resolve_approval

**Traces**: api_list_traces, api_get_trace, api_search_traces

**A2A Discovery**: api_get_agent_card, api_get_team_card, api_get_workflow_card
(returns .well-known/agent-card.json; A2A v1 uses JSON-RPC 2.0 — tools handle the envelope)

**A2A v1 Agents**: api_a2a_send_agent_message, api_a2a_get_agent_task, api_a2a_cancel_agent_task
**A2A v1 Teams**: api_a2a_send_team_message, api_a2a_get_team_task, api_a2a_cancel_team_task
**A2A v1 Workflows**: api_a2a_send_workflow_message · **A2A Legacy**: api_a2a_legacy_send

**Slack Interface**: api_slack_post_event (POST /slack/events — only active when SLACK_BOT_TOKEN set)
**WhatsApp Interface**: api_whatsapp_status, api_whatsapp_verify_webhook, api_whatsapp_post_webhook
**Telegram Interface**: api_telegram_status, api_telegram_post_update (needs TELEGRAM_BOT_TOKEN)
**Discord Interface**: api_discord_status, api_discord_post_interaction (needs DISCORD_PUBLIC_KEY + DISCORD_BOT_TOKEN)

**Components**: api_list_components, api_create_component, api_list_registry

**Admin**: api_get_metrics, api_migrate_all_databases, api_get_available_models,
api_health_check

## Approval Flow
When the user asks to delete a resource, call `delete_resource`. The request
will pause for human approval — do not retry; wait for the operator to approve
or reject from the AgentOS Control Plane.

""",
    knowledge=assistant_knowledge,
    search_knowledge=True,
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
