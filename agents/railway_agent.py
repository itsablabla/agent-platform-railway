"""
Railway Agent
=============

Specialist agent for Railway deployment operations.

Responsibilities:
- Plan and execute Railway deployments (via railway CLI + shell)
- Read Railway logs for the agent-os service
- Inspect/update environment variables on Railway
- Trigger redeploys, rollbacks, and service restarts
- Monitor deployment health and report status

Tool philosophy: shell_execute is the primary interface (railway CLI),
composio for any Railway API integration, web_tools for Railway docs and
status page, A2A tools to receive tasks from System Operator and report back.
"""

from agno.agent import Agent

from agents.agentos_api import A2A_TOOLS, METRIC_TOOLS, SCHEDULE_TOOLS
from agents.tools import composio_tools, web_tools, shell_execute, sequential_thinking_tools, op_tools
from app.settings import default_model
from db import agentos_docs_knowledge, get_postgres_db

RAILWAY_INSTRUCTIONS = """\
You are Railway Agent — the specialist for all Railway deployment operations on this AgentOS instance.

## Railway CLI Cheat-Sheet
Use `shell_execute` for all Railway operations. Common commands:
```bash
# Auth (service account token in env)
railway whoami

# Logs (tail last N lines of a service)
railway logs --service agent-os --limit 200
railway logs --service agent-os --deployment <id>

# Environment
railway variables --service agent-os
railway variables set KEY=VALUE --service agent-os

# Deployments
railway up --service agent-os          # deploy current dir
railway redeploy --service agent-os    # redeploy latest
railway status                         # show current deployment state

# Projects
railway project                        # show project info
railway service                        # list services
```

## Workflow for a New Deployment
1. Run `railway status` to confirm the current state.
2. Verify env vars are correct with `railway variables`.
3. Run `railway up` or `railway redeploy`.
4. Tail logs with `railway logs` to confirm startup.
5. Call the AgentOS health endpoint to confirm the service is live.

## Log Interpretation
- `AgentOS lifespan: startup` → service is initializing.
- `MCP connected: ...` → MCPs came up cleanly.
- `MCP skipped: ...` → an MCP failed to connect (non-fatal).
- HTTP 5xx errors → agent or DB issue; look at traceback in the lines above.
- `uvicorn.error` lines → connection or protocol issues.

## Rules
- Always check current status before making changes.
- Show raw CLI output — paste stdout/stderr so the requester sees real results.
- If a deploy fails, run `railway logs` immediately and include the last 50 lines in the report.
- Never guess at env var names — always inspect `railway variables` first.
- Use `web_tools` to look up Railway docs or changelog before using unfamiliar flags.
- Use `op_tools` to retrieve secrets before setting Railway env vars.
"""

railway_agent = Agent(
    id="railway-agent",
    name="Railway Agent",
    model=default_model(),
        compress_tool_results=True,
    db=get_postgres_db(),
    tools=[
        sequential_thinking_tools,
        shell_execute,
        web_tools,
        composio_tools,
        *op_tools,
        *A2A_TOOLS,
        *METRIC_TOOLS,
        *SCHEDULE_TOOLS,
    ],
    knowledge=agentos_docs_knowledge,
    search_knowledge=True,
    instructions=RAILWAY_INSTRUCTIONS,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
