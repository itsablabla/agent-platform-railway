"""
AgentOS REST API Tools
======================
Every AgentOS HTTP endpoint exposed as an @tool for the admin_ops agent.

Base URL: AGENTOS_URL env (default http://127.0.0.1:8000)
Auth:     OS_SECURITY_KEY env sent as Bearer token when set.
Streaming endpoints are excluded — they return SSE, not JSON.
"""

from __future__ import annotations

import json
import os
from typing import Optional

import httpx
from agno.tools import tool

_BASE = os.getenv("AGENTOS_URL", "http://127.0.0.1:8000")
_KEY = os.getenv("OS_SECURITY_KEY", "")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _h() -> dict:
    return {"Authorization": f"Bearer {_KEY}"} if _KEY else {}


def _r(resp: httpx.Response) -> str:
    try:
        return json.dumps(resp.json(), indent=2)
    except Exception:
        return resp.text


def _get(path: str, **params) -> str:
    p = {k: v for k, v in params.items() if v is not None}
    return _r(httpx.get(f"{_BASE}{path}", params=p or None, headers=_h(), timeout=30))


def _post(path: str, body: dict | None = None) -> str:
    b = {k: v for k, v in (body or {}).items() if v is not None}
    return _r(httpx.post(f"{_BASE}{path}", json=b or None, headers=_h(), timeout=60))


def _put(path: str, body: dict | None = None) -> str:
    b = {k: v for k, v in (body or {}).items() if v is not None}
    return _r(httpx.put(f"{_BASE}{path}", json=b or None, headers=_h(), timeout=30))


def _patch(path: str, body: dict | None = None) -> str:
    b = {k: v for k, v in (body or {}).items() if v is not None}
    return _r(httpx.patch(f"{_BASE}{path}", json=b or None, headers=_h(), timeout=30))


def _delete(path: str, body: dict | None = None) -> str:
    b = {k: v for k, v in (body or {}).items() if v is not None}
    req = httpx.delete(f"{_BASE}{path}", json=b or None, headers=_h(), timeout=30)
    return _r(req)


# ===========================================================================
# HEALTH & HOME
# ===========================================================================

@tool
def api_health_check() -> str:
    """Check if AgentOS is healthy and running."""
    return _get("/health")


@tool
def api_info() -> str:
    """Get general API information and version."""
    return _get("/")


# ===========================================================================
# CORE
# ===========================================================================

@tool
def api_get_available_models() -> str:
    """List all available LLM models registered with AgentOS."""
    return _get("/models")


@tool
def api_get_os_configuration() -> str:
    """Get the current AgentOS configuration."""
    return _get("/config")


# ===========================================================================
# AGENTS
# ===========================================================================

@tool
def api_list_agents() -> str:
    """List all registered agents in AgentOS."""
    return _get("/agents")


@tool
def api_get_agent(agent_id: str) -> str:
    """Get details for a specific agent by ID."""
    return _get(f"/agents/{agent_id}")


@tool
def api_create_agent_run(
    agent_id: str,
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    stream: bool = False,
    background: bool = False,
    version: Optional[str] = None,
) -> str:
    """Start a new run for an agent. Set background=True to run async without waiting."""
    return _post(f"/agents/{agent_id}/runs", {
        "message": message,
        "session_id": session_id,
        "user_id": user_id,
        "stream": stream,
        "background": background,
        "version": version,
    })


@tool
def api_list_agent_runs(
    agent_id: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List all runs for a specific agent."""
    return _get(f"/agents/{agent_id}/runs", session_id=session_id, user_id=user_id, limit=limit, page=page)


@tool
def api_get_agent_run(agent_id: str, run_id: str) -> str:
    """Get details for a specific agent run."""
    return _get(f"/agents/{agent_id}/runs/{run_id}")


@tool
def api_continue_agent_run(
    agent_id: str,
    run_id: str,
    message: Optional[str] = None,
) -> str:
    """Continue a paused or interrupted agent run (e.g. after approval)."""
    return _post(f"/agents/{agent_id}/runs/{run_id}/continue", {"message": message})


@tool
def api_cancel_agent_run(agent_id: str, run_id: str) -> str:
    """Cancel an in-progress agent run."""
    return _post(f"/agents/{agent_id}/runs/{run_id}/cancel")


# ===========================================================================
# TEAMS
# ===========================================================================

@tool
def api_list_teams() -> str:
    """List all registered teams in AgentOS."""
    return _get("/teams")


@tool
def api_get_team(team_id: str) -> str:
    """Get details for a specific team by ID."""
    return _get(f"/teams/{team_id}")


@tool
def api_create_team_run(
    team_id: str,
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    stream: bool = False,
    background: bool = False,
) -> str:
    """Start a new run for a team."""
    return _post(f"/teams/{team_id}/runs", {
        "message": message,
        "session_id": session_id,
        "user_id": user_id,
        "stream": stream,
        "background": background,
    })


@tool
def api_list_team_runs(
    team_id: str,
    session_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """List all runs for a specific team."""
    return _get(f"/teams/{team_id}/runs", session_id=session_id, limit=limit)


@tool
def api_get_team_run(team_id: str, run_id: str) -> str:
    """Get details for a specific team run."""
    return _get(f"/teams/{team_id}/runs/{run_id}")


@tool
def api_cancel_team_run(team_id: str, run_id: str) -> str:
    """Cancel an in-progress team run."""
    return _post(f"/teams/{team_id}/runs/{run_id}/cancel")


# ===========================================================================
# WORKFLOWS
# ===========================================================================

@tool
def api_list_workflows() -> str:
    """List all registered workflows in AgentOS."""
    return _get("/workflows")


@tool
def api_get_workflow(workflow_id: str) -> str:
    """Get details for a specific workflow by ID."""
    return _get(f"/workflows/{workflow_id}")


@tool
def api_execute_workflow(
    workflow_id: str,
    message: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    background: bool = False,
) -> str:
    """Execute a workflow."""
    return _post(f"/workflows/{workflow_id}/runs", {
        "message": message,
        "session_id": session_id,
        "user_id": user_id,
        "background": background,
    })


@tool
def api_get_workflow_run(workflow_id: str, run_id: str) -> str:
    """Get details for a specific workflow run."""
    return _get(f"/workflows/{workflow_id}/runs/{run_id}")


@tool
def api_cancel_workflow_run(workflow_id: str, run_id: str) -> str:
    """Cancel an in-progress workflow run."""
    return _post(f"/workflows/{workflow_id}/runs/{run_id}/cancel")


# ===========================================================================
# SESSIONS
# ===========================================================================

@tool
def api_list_sessions(
    component_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_name: Optional[str] = None,
    type: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> str:
    """List sessions. Filter by component_id, user_id, session_name, or type."""
    return _get("/sessions", component_id=component_id, user_id=user_id,
                session_name=session_name, type=type, limit=limit, page=page,
                sort_by=sort_by, sort_order=sort_order)


@tool
def api_create_session(
    agent_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_name: Optional[str] = None,
) -> str:
    """Create a new session."""
    return _post("/sessions", {"agent_id": agent_id, "user_id": user_id, "session_name": session_name})


@tool
def api_get_session(session_id: str) -> str:
    """Get a session by ID."""
    return _get(f"/sessions/{session_id}")


@tool
def api_update_session(session_id: str, session_data: str) -> str:
    """Update session metadata. session_data should be a JSON string of fields to update."""
    try:
        body = json.loads(session_data)
    except Exception:
        return f"Error: session_data must be valid JSON, got: {session_data}"
    return _put(f"/sessions/{session_id}", body)


@tool
def api_rename_session(session_id: str, session_name: str) -> str:
    """Rename a session."""
    return _patch(f"/sessions/{session_id}", {"session_name": session_name})


@tool
def api_delete_session(session_id: str) -> str:
    """Delete a session by ID."""
    return _delete(f"/sessions/{session_id}")


@tool
def api_delete_multiple_sessions(session_ids: str) -> str:
    """Delete multiple sessions. session_ids should be a JSON array string e.g. '[\"id1\",\"id2\"]'."""
    try:
        ids = json.loads(session_ids)
    except Exception:
        return f"Error: session_ids must be a JSON array string, got: {session_ids}"
    return _delete("/sessions", {"session_ids": ids})


@tool
def api_get_session_runs(session_id: str, limit: Optional[int] = None) -> str:
    """Get all runs within a session."""
    return _get(f"/sessions/{session_id}/runs", limit=limit)


@tool
def api_get_run_by_id(session_id: str, run_id: str) -> str:
    """Get a specific run by ID within a session."""
    return _get(f"/sessions/{session_id}/runs/{run_id}")


# ===========================================================================
# MEMORY
# ===========================================================================

@tool
def api_list_memories(
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List memories. Filter by user_id or agent_id."""
    return _get("/memories", user_id=user_id, agent_id=agent_id, limit=limit, page=page)


@tool
def api_get_memory(memory_id: str) -> str:
    """Get a specific memory by ID."""
    return _get(f"/memories/{memory_id}")


@tool
def api_create_memory(
    memory: str,
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    topics: Optional[str] = None,
) -> str:
    """Create a new memory. topics should be a JSON array string if provided."""
    body: dict = {"memory": memory}
    if user_id:
        body["user_id"] = user_id
    if agent_id:
        body["agent_id"] = agent_id
    if topics:
        try:
            body["topics"] = json.loads(topics)
        except Exception:
            body["topics"] = [topics]
    return _post("/memories", body)


@tool
def api_update_memory(
    memory_id: str,
    memory: str,
    topics: Optional[str] = None,
) -> str:
    """Update a memory by ID."""
    body: dict = {"memory": memory}
    if topics:
        try:
            body["topics"] = json.loads(topics)
        except Exception:
            body["topics"] = [topics]
    return _put(f"/memories/{memory_id}", body)


@tool
def api_delete_memory(memory_id: str) -> str:
    """Delete a memory by ID."""
    return _delete(f"/memories/{memory_id}")


@tool
def api_delete_multiple_memories(memory_ids: str) -> str:
    """Delete multiple memories. memory_ids should be a JSON array string."""
    try:
        ids = json.loads(memory_ids)
    except Exception:
        return f"Error: memory_ids must be a JSON array string, got: {memory_ids}"
    return _delete("/memories", {"memory_ids": ids})


@tool
def api_get_memory_topics(user_id: Optional[str] = None) -> str:
    """Get all memory topics, optionally filtered by user_id."""
    return _get("/memories/topics", user_id=user_id)


@tool
def api_get_user_memory_statistics(user_id: Optional[str] = None) -> str:
    """Get memory statistics for a user."""
    return _get("/memories/stats", user_id=user_id)


@tool
def api_optimize_user_memories(user_id: str) -> str:
    """Optimize and consolidate memories for a user."""
    return _post("/memories/optimize", {"user_id": user_id})


# ===========================================================================
# KNOWLEDGE
# ===========================================================================

@tool
def api_list_knowledge_content(
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List all knowledge content."""
    return _get("/knowledge/content", limit=limit, page=page)


@tool
def api_get_knowledge_content(content_id: str) -> str:
    """Get a specific knowledge content item by ID."""
    return _get(f"/knowledge/content/{content_id}")


@tool
def api_upload_knowledge_content(
    name: str,
    text_content: Optional[str] = None,
    url: Optional[str] = None,
    description: Optional[str] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> str:
    """Upload text or URL content to the knowledge base."""
    return _post("/knowledge/content", {
        "name": name,
        "text_content": text_content,
        "url": url,
        "description": description,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
    })


@tool
def api_upload_remote_knowledge_content(
    url: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Upload content from a remote URL to the knowledge base."""
    return _post("/knowledge/content/remote", {"url": url, "name": name, "description": description})


@tool
def api_update_knowledge_content(
    content_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Update knowledge content metadata by ID."""
    return _put(f"/knowledge/content/{content_id}", {"name": name, "description": description})


@tool
def api_delete_knowledge_content(content_id: str) -> str:
    """Delete a specific knowledge content item by ID."""
    return _delete(f"/knowledge/content/{content_id}")


@tool
def api_delete_all_knowledge_content() -> str:
    """Delete ALL knowledge content. This is irreversible."""
    return _delete("/knowledge/content")


@tool
def api_list_knowledge_sources(limit: Optional[int] = None) -> str:
    """List all knowledge content sources."""
    return _get("/knowledge/sources", limit=limit)


@tool
def api_list_files_in_knowledge_source(source_id: str) -> str:
    """List all files within a specific knowledge source."""
    return _get(f"/knowledge/sources/{source_id}/files")


@tool
def api_get_knowledge_content_status(content_id: str) -> str:
    """Get the processing status of a knowledge content item."""
    return _get(f"/knowledge/content/{content_id}/status")


@tool
def api_get_knowledge_config() -> str:
    """Get the knowledge base configuration."""
    return _get("/knowledge/config")


@tool
def api_search_knowledge(
    query: str,
    limit: Optional[int] = None,
) -> str:
    """Search the knowledge base with a query."""
    return _post("/knowledge/search", {"query": query, "limit": limit})


# ===========================================================================
# SCHEDULES
# ===========================================================================

@tool
def api_list_schedules(
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List all schedules."""
    return _get("/schedules", limit=limit, page=page)


@tool
def api_get_schedule(schedule_id: str) -> str:
    """Get a specific schedule by ID."""
    return _get(f"/schedules/{schedule_id}")


@tool
def api_create_schedule(
    name: str,
    cron_expr: str,
    endpoint: str,
    method: str = "POST",
    description: Optional[str] = None,
    payload: Optional[str] = None,
    timezone: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
    max_retries: Optional[int] = None,
) -> str:
    """Create a schedule. cron_expr e.g. '0 9 * * 1-5'. payload should be a JSON string if provided."""
    body: dict = {
        "name": name,
        "cron_expr": cron_expr,
        "endpoint": endpoint,
        "method": method,
        "description": description,
        "timezone": timezone,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
    }
    if payload:
        try:
            body["payload"] = json.loads(payload)
        except Exception:
            body["payload"] = payload
    return _post("/schedules", body)


@tool
def api_update_schedule(
    schedule_id: str,
    name: Optional[str] = None,
    cron_expr: Optional[str] = None,
    description: Optional[str] = None,
    payload: Optional[str] = None,
    timezone: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
    max_retries: Optional[int] = None,
) -> str:
    """Update an existing schedule."""
    body: dict = {
        "name": name,
        "cron_expr": cron_expr,
        "description": description,
        "timezone": timezone,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
    }
    if payload:
        try:
            body["payload"] = json.loads(payload)
        except Exception:
            body["payload"] = payload
    return _put(f"/schedules/{schedule_id}", body)


@tool
def api_delete_schedule(schedule_id: str) -> str:
    """Delete a schedule by ID."""
    return _delete(f"/schedules/{schedule_id}")


@tool
def api_enable_schedule(schedule_id: str) -> str:
    """Enable a disabled schedule."""
    return _post(f"/schedules/{schedule_id}/enable")


@tool
def api_disable_schedule(schedule_id: str) -> str:
    """Disable an active schedule without deleting it."""
    return _post(f"/schedules/{schedule_id}/disable")


@tool
def api_trigger_schedule(schedule_id: str) -> str:
    """Manually trigger a schedule to run immediately."""
    return _post(f"/schedules/{schedule_id}/trigger")


@tool
def api_list_schedule_runs(
    schedule_id: str,
    limit: Optional[int] = None,
) -> str:
    """List all runs for a specific schedule."""
    return _get(f"/schedules/{schedule_id}/runs", limit=limit)


@tool
def api_get_schedule_run(schedule_id: str, run_id: str) -> str:
    """Get details for a specific schedule run."""
    return _get(f"/schedules/{schedule_id}/runs/{run_id}")


# ===========================================================================
# APPROVALS
# ===========================================================================

@tool
def api_list_approvals(
    status: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List all pending/resolved approvals. Filter by status ('pending', 'approved', 'rejected')."""
    return _get("/approvals", status=status, agent_id=agent_id, limit=limit, page=page)


@tool
def api_get_approval(approval_id: str) -> str:
    """Get a specific approval request by ID."""
    return _get(f"/approvals/{approval_id}")


@tool
def api_get_approval_count(status: Optional[str] = None) -> str:
    """Get the count of approval requests, optionally filtered by status."""
    return _get("/approvals/count", status=status)


@tool
def api_get_approval_status(approval_id: str) -> str:
    """Get the current status of a specific approval request."""
    return _get(f"/approvals/{approval_id}/status")


@tool
def api_resolve_approval(
    approval_id: str,
    status: str,
    resolved_by: Optional[str] = None,
    resolution_data: Optional[str] = None,
) -> str:
    """Resolve an approval request. status must be 'approved' or 'rejected'.
    resolution_data should be a JSON string with any extra context."""
    body: dict = {"status": status, "resolved_by": resolved_by}
    if resolution_data:
        try:
            body["resolution_data"] = json.loads(resolution_data)
        except Exception:
            body["resolution_data"] = resolution_data
    return _post(f"/approvals/{approval_id}/resolve", body)


@tool
def api_delete_approval(approval_id: str) -> str:
    """Delete an approval request by ID."""
    return _delete(f"/approvals/{approval_id}")


# ===========================================================================
# TRACES
# ===========================================================================

@tool
def api_list_traces(
    agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List traces. Filter by agent_id or session_id."""
    return _get("/traces", agent_id=agent_id, session_id=session_id, limit=limit, page=page)


@tool
def api_get_trace(trace_id: str) -> str:
    """Get trace or span detail by ID."""
    return _get(f"/traces/{trace_id}")


@tool
def api_get_trace_statistics(session_id: str) -> str:
    """Get trace statistics aggregated by session."""
    return _get("/traces/stats", session_id=session_id)


@tool
def api_search_traces(
    query: str,
    filters: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """Search traces with advanced filters. filters should be a JSON string if provided."""
    body: dict = {"query": query, "limit": limit}
    if filters:
        try:
            body["filters"] = json.loads(filters)
        except Exception:
            body["filters"] = filters
    return _post("/traces/search", body)


@tool
def api_get_trace_filter_schema() -> str:
    """Get the schema for trace filter options."""
    return _get("/traces/filters")


# ===========================================================================
# A2A (Agent-to-Agent)
# ===========================================================================

@tool
def api_get_agent_card(agent_id: str) -> str:
    """Get the A2A agent card (capability/skill manifest) for an agent."""
    return _get(f"/a2a/agents/{agent_id}/.well-known/agent-card.json")


@tool
def api_get_team_card(team_id: str) -> str:
    """Get the A2A agent card (capability manifest) for a team."""
    return _get(f"/a2a/teams/{team_id}/.well-known/agent-card.json")


@tool
def api_get_workflow_card(workflow_id: str) -> str:
    """Get the A2A agent card (capability manifest) for a workflow."""
    return _get(f"/a2a/workflows/{workflow_id}/.well-known/agent-card.json")


def _a2a_body(method: str, message: str, context_id: Optional[str], request_id: str = "1") -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                **({"contextId": context_id} if context_id else {}),
            }
        },
    }


@tool
def api_a2a_send_agent_message(
    agent_id: str,
    message: str,
    context_id: Optional[str] = None,
    blocking: bool = True,
) -> str:
    """Send a message to an agent via the A2A v1 JSON-RPC protocol (non-streaming).
    Returns a task object with id, status, and history. blocking=False runs in background."""
    body = _a2a_body("message/send", message, context_id)
    if not blocking:
        body["params"]["configuration"] = {"blocking": False}
    return _post(f"/a2a/agents/{agent_id}/v1/message:send", body)


@tool
def api_a2a_get_agent_task(
    agent_id: str,
    task_id: str,
    context_id: Optional[str] = None,
) -> str:
    """Get the status and result of an A2A agent task by task_id."""
    body = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tasks/get",
        "params": {"id": task_id, **({"contextId": context_id} if context_id else {})},
    }
    return _post(f"/a2a/agents/{agent_id}/v1/tasks:get", body)


@tool
def api_a2a_cancel_agent_task(
    agent_id: str,
    task_id: str,
    context_id: Optional[str] = None,
) -> str:
    """Cancel an in-progress A2A agent task."""
    body = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tasks/cancel",
        "params": {"id": task_id, **({"contextId": context_id} if context_id else {})},
    }
    return _post(f"/a2a/agents/{agent_id}/v1/tasks:cancel", body)


@tool
def api_a2a_send_team_message(
    team_id: str,
    message: str,
    context_id: Optional[str] = None,
    blocking: bool = True,
) -> str:
    """Send a message to a team via the A2A v1 JSON-RPC protocol (non-streaming)."""
    body = _a2a_body("message/send", message, context_id)
    if not blocking:
        body["params"]["configuration"] = {"blocking": False}
    return _post(f"/a2a/teams/{team_id}/v1/message:send", body)


@tool
def api_a2a_get_team_task(
    team_id: str,
    task_id: str,
    context_id: Optional[str] = None,
) -> str:
    """Get the status and result of an A2A team task by task_id."""
    body = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tasks/get",
        "params": {"id": task_id, **({"contextId": context_id} if context_id else {})},
    }
    return _post(f"/a2a/teams/{team_id}/v1/tasks:get", body)


@tool
def api_a2a_cancel_team_task(
    team_id: str,
    task_id: str,
    context_id: Optional[str] = None,
) -> str:
    """Cancel an in-progress A2A team task."""
    body = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tasks/cancel",
        "params": {"id": task_id, **({"contextId": context_id} if context_id else {})},
    }
    return _post(f"/a2a/teams/{team_id}/v1/tasks:cancel", body)


@tool
def api_a2a_send_workflow_message(
    workflow_id: str,
    message: str,
    context_id: Optional[str] = None,
    blocking: bool = True,
) -> str:
    """Send a message to a workflow via the A2A v1 JSON-RPC protocol (non-streaming)."""
    body = _a2a_body("message/send", message, context_id)
    if not blocking:
        body["params"]["configuration"] = {"blocking": False}
    return _post(f"/a2a/workflows/{workflow_id}/v1/message:send", body)


@tool
def api_a2a_legacy_send(
    message: str,
    agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """Legacy A2A send endpoint — routes to any agent. Prefer api_a2a_send_agent_message for new code."""
    return _post("/a2a/message/send", {
        "message": {"role": "user", "content": message},
        "agent_id": agent_id,
        "session_id": session_id,
    })


# ===========================================================================
# SLACK INTERFACE  (/slack prefix — active only when SLACK_BOT_TOKEN is set)
# ===========================================================================

@tool
def api_slack_post_event(payload: str) -> str:
    """Post a Slack event to the AgentOS Slack interface webhook endpoint.
    payload must be a JSON string matching the Slack Events API payload format.
    Use for testing the Slack integration or replaying events."""
    try:
        body = json.loads(payload)
    except Exception:
        return f"Error: payload must be valid JSON, got: {payload}"
    return _post("/slack/events", body)


# ===========================================================================
# WHATSAPP INTERFACE  (/whatsapp prefix — active only when WA tokens are set)
# ===========================================================================

@tool
def api_whatsapp_status() -> str:
    """Check whether the WhatsApp interface is active and healthy."""
    return _get("/whatsapp/status")


@tool
def api_whatsapp_verify_webhook(
    hub_mode: str,
    hub_verify_token: str,
    hub_challenge: str,
) -> str:
    """Perform the WhatsApp webhook verification challenge-response flow.
    hub_mode should be 'subscribe', hub_verify_token is the token you set in Meta,
    hub_challenge is any string — the server echoes it back on success."""
    return _get("/whatsapp/webhook",
                **{"hub.mode": hub_mode, "hub.verify_token": hub_verify_token,
                   "hub.challenge": hub_challenge})


@tool
def api_whatsapp_post_webhook(payload: str) -> str:
    """Post a WhatsApp webhook event to the AgentOS WhatsApp interface.
    payload must be a JSON string in the Meta WhatsApp Business API webhook format.
    Use for testing the WhatsApp integration or replaying events."""
    try:
        body = json.loads(payload)
    except Exception:
        return f"Error: payload must be valid JSON, got: {payload}"
    return _post("/whatsapp/webhook", body)


# ===========================================================================
# COMPONENTS / REGISTRY
# ===========================================================================

@tool
def api_list_components(
    component_type: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List components. Filter by component_type (e.g. 'agent', 'model', 'tool')."""
    return _get("/components", component_type=component_type, limit=limit, page=page)


@tool
def api_get_component(component_id: str) -> str:
    """Get a specific component by ID."""
    return _get(f"/components/{component_id}")


@tool
def api_create_component(
    name: str,
    component_type: str,
    config: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Create a new component. config should be a JSON string if provided."""
    body: dict = {"name": name, "type": component_type, "description": description}
    if config:
        try:
            body["config"] = json.loads(config)
        except Exception:
            body["config"] = config
    return _post("/components", body)


@tool
def api_update_component(
    component_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    config: Optional[str] = None,
) -> str:
    """Update a component by ID."""
    body: dict = {"name": name, "description": description}
    if config:
        try:
            body["config"] = json.loads(config)
        except Exception:
            body["config"] = config
    return _put(f"/components/{component_id}", body)


@tool
def api_delete_component(component_id: str) -> str:
    """Delete a component by ID."""
    return _delete(f"/components/{component_id}")


@tool
def api_list_component_configs(component_id: str) -> str:
    """List all config versions for a component."""
    return _get(f"/components/{component_id}/configs")


@tool
def api_get_current_component_config(component_id: str) -> str:
    """Get the currently active config for a component."""
    return _get(f"/components/{component_id}/configs/current")


@tool
def api_get_component_config_version(component_id: str, version: str) -> str:
    """Get a specific config version for a component."""
    return _get(f"/components/{component_id}/configs/{version}")


@tool
def api_create_component_config_version(
    component_id: str,
    config: str,
    version: Optional[str] = None,
) -> str:
    """Create a new config version for a component. config must be a JSON string."""
    try:
        cfg = json.loads(config)
    except Exception:
        return f"Error: config must be valid JSON, got: {config}"
    return _post(f"/components/{component_id}/configs", {"config": cfg, "version": version})


@tool
def api_update_draft_component_config(
    component_id: str,
    version: str,
    config: str,
) -> str:
    """Update the draft config for a component version. config must be a JSON string."""
    try:
        cfg = json.loads(config)
    except Exception:
        return f"Error: config must be valid JSON, got: {config}"
    return _put(f"/components/{component_id}/configs/{version}", {"config": cfg})


@tool
def api_delete_component_config_version(component_id: str, version: str) -> str:
    """Delete a specific config version for a component."""
    return _delete(f"/components/{component_id}/configs/{version}")


@tool
def api_set_current_component_config(component_id: str, version: str) -> str:
    """Set a specific config version as the current active version."""
    return _post(f"/components/{component_id}/configs/{version}/set-current")


# ===========================================================================
# REGISTRY
# ===========================================================================

@tool
def api_list_registry(
    resource_type: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """List the AgentOS registry. Filter by resource_type (e.g. 'model', 'agent', 'tool')."""
    return _get("/registry", resource_type=resource_type, limit=limit)


# ===========================================================================
# EVALS
# ===========================================================================

@tool
def api_list_eval_runs(
    agent_id: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
) -> str:
    """List evaluation runs, optionally filtered by agent_id."""
    return _get("/evals", agent_id=agent_id, limit=limit, page=page)


@tool
def api_get_eval_run(eval_id: str) -> str:
    """Get a specific evaluation run by ID."""
    return _get(f"/evals/{eval_id}")


@tool
def api_execute_evaluation(
    agent_id: str,
    eval_config: Optional[str] = None,
) -> str:
    """Execute an evaluation for an agent. eval_config should be a JSON string if provided."""
    body: dict = {"agent_id": agent_id}
    if eval_config:
        try:
            body["config"] = json.loads(eval_config)
        except Exception:
            body["config"] = eval_config
    return _post("/evals", body)


@tool
def api_update_eval_run(
    eval_id: str,
    status: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Update an evaluation run (e.g. add notes or change status)."""
    return _put(f"/evals/{eval_id}", {"status": status, "notes": notes})


@tool
def api_delete_eval_runs(
    agent_id: Optional[str] = None,
    eval_ids: Optional[str] = None,
) -> str:
    """Delete evaluation runs. eval_ids should be a JSON array string if provided."""
    body: dict = {"agent_id": agent_id}
    if eval_ids:
        try:
            body["eval_ids"] = json.loads(eval_ids)
        except Exception:
            return f"Error: eval_ids must be a JSON array string, got: {eval_ids}"
    return _delete("/evals", body)


# ===========================================================================
# DATABASE
# ===========================================================================

@tool
def api_migrate_all_databases() -> str:
    """Run migrations for all AgentOS databases."""
    return _post("/database/migrate")


@tool
def api_migrate_database(db_id: str) -> str:
    """Run migrations for a specific database by ID."""
    return _post(f"/database/migrate/{db_id}")


# ===========================================================================
# METRICS
# ===========================================================================

@tool
def api_get_metrics() -> str:
    """Get AgentOS usage and performance metrics."""
    return _get("/metrics")


@tool
def api_refresh_metrics() -> str:
    """Refresh/recalculate AgentOS metrics."""
    return _post("/metrics/refresh")


# ===========================================================================
# AG-UI
# ===========================================================================

@tool
def api_agui_status() -> str:
    """Get the AG-UI integration status."""
    return _get("/agui/status")


# ===========================================================================
# Exported list for import convenience
# ===========================================================================

AGENTOS_API_TOOLS = [
    # Health & Home
    api_health_check,
    api_info,
    # Core
    api_get_available_models,
    api_get_os_configuration,
    # Agents
    api_list_agents,
    api_get_agent,
    api_create_agent_run,
    api_list_agent_runs,
    api_get_agent_run,
    api_continue_agent_run,
    api_cancel_agent_run,
    # Teams
    api_list_teams,
    api_get_team,
    api_create_team_run,
    api_list_team_runs,
    api_get_team_run,
    api_cancel_team_run,
    # Workflows
    api_list_workflows,
    api_get_workflow,
    api_execute_workflow,
    api_get_workflow_run,
    api_cancel_workflow_run,
    # Sessions
    api_list_sessions,
    api_create_session,
    api_get_session,
    api_update_session,
    api_rename_session,
    api_delete_session,
    api_delete_multiple_sessions,
    api_get_session_runs,
    api_get_run_by_id,
    # Memory
    api_list_memories,
    api_get_memory,
    api_create_memory,
    api_update_memory,
    api_delete_memory,
    api_delete_multiple_memories,
    api_get_memory_topics,
    api_get_user_memory_statistics,
    api_optimize_user_memories,
    # Knowledge
    api_list_knowledge_content,
    api_get_knowledge_content,
    api_upload_knowledge_content,
    api_upload_remote_knowledge_content,
    api_update_knowledge_content,
    api_delete_knowledge_content,
    api_delete_all_knowledge_content,
    api_list_knowledge_sources,
    api_list_files_in_knowledge_source,
    api_get_knowledge_content_status,
    api_get_knowledge_config,
    api_search_knowledge,
    # Schedules
    api_list_schedules,
    api_get_schedule,
    api_create_schedule,
    api_update_schedule,
    api_delete_schedule,
    api_enable_schedule,
    api_disable_schedule,
    api_trigger_schedule,
    api_list_schedule_runs,
    api_get_schedule_run,
    # Approvals
    api_list_approvals,
    api_get_approval,
    api_get_approval_count,
    api_get_approval_status,
    api_resolve_approval,
    api_delete_approval,
    # Traces
    api_list_traces,
    api_get_trace,
    api_get_trace_statistics,
    api_search_traces,
    api_get_trace_filter_schema,
    # A2A — Discovery
    api_get_agent_card,
    api_get_team_card,
    api_get_workflow_card,
    # A2A — Agents (v1 JSON-RPC)
    api_a2a_send_agent_message,
    api_a2a_get_agent_task,
    api_a2a_cancel_agent_task,
    # A2A — Teams (v1 JSON-RPC)
    api_a2a_send_team_message,
    api_a2a_get_team_task,
    api_a2a_cancel_team_task,
    # A2A — Workflows (v1 JSON-RPC)
    api_a2a_send_workflow_message,
    # A2A — Legacy
    api_a2a_legacy_send,
    # Slack Interface
    api_slack_post_event,
    # WhatsApp Interface
    api_whatsapp_status,
    api_whatsapp_verify_webhook,
    api_whatsapp_post_webhook,
    # Components
    api_list_components,
    api_get_component,
    api_create_component,
    api_update_component,
    api_delete_component,
    api_list_component_configs,
    api_get_current_component_config,
    api_get_component_config_version,
    api_create_component_config_version,
    api_update_draft_component_config,
    api_delete_component_config_version,
    api_set_current_component_config,
    # Registry
    api_list_registry,
    # Evals
    api_list_eval_runs,
    api_get_eval_run,
    api_execute_evaluation,
    api_update_eval_run,
    api_delete_eval_runs,
    # Database
    api_migrate_all_databases,
    api_migrate_database,
    # Metrics
    api_get_metrics,
    api_refresh_metrics,
    # AG-UI
    api_agui_status,
]
