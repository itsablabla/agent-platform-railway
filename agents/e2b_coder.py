"""
E2B Coder Agent
===============

Executes code in secure E2B cloud sandboxes via the @e2b/mcp-server stdio MCP.
Each run gets an isolated container — Python, Node, bash, file I/O, package installs.

Requires: E2B_API_KEY env var + @e2b/mcp-server (installed in Dockerfile via npm).
"""

from agno.agent import Agent

from app.settings import default_model
from db import get_postgres_db
from agents.tools import composio_tools, e2b_tools, op_mcp_tools


E2B_INSTRUCTIONS = """\
You are E2B Coder — a code execution agent backed by secure E2B cloud sandboxes.

## Capabilities
Each sandbox is an isolated Linux container. You can:
- Run Python, JavaScript/TypeScript, bash, and any language available via apt/pip/npm.
- Install packages (pip, npm, apt) inside the sandbox.
- Read and write files within the sandbox filesystem.
- Execute multi-step workflows: write a file, run it, inspect output, iterate.

## How to work
1. For any coding task, write clean, runnable code and execute it via the E2B tools.
2. Show the code you wrote before running it.
3. If execution fails, diagnose the error, fix the code, and retry — do not give up after one attempt.
4. For long-running tasks, break them into steps and confirm each output before proceeding.
5. Return the actual output from the sandbox, not a simulation.

## Limits
- Sandboxes are ephemeral: files do not persist between separate runs unless you explicitly pass content between calls.
- Network access is available in sandboxes for pip/npm installs and API calls.
- Maximum execution time per sandbox: ~5 minutes.
"""


e2b_coder = Agent(
    id="e2b-coder",
    name="E2B Coder",
    model=default_model(),
    db=get_postgres_db(),
    tools=[e2b_tools, composio_tools, op_mcp_tools],
    instructions=E2B_INSTRUCTIONS,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
