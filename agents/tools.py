"""
Shared MCP Toolkits
===================

All MCP-based toolkits in one place to avoid circular imports.

HTTP-based:
- Web Search (Parallel.ai)
- Composio (SaaS integrations)

stdio-based:
- E2B (code execution sandboxes via npx)
- Sequential Thinking

Direct Function tools:
- 1Password (op CLI v2 with OP_SERVICE_ACCOUNT_TOKEN)
- Shell execution
"""

import os
from os import getenv

from agno.tools import tool
from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams

# ---------------------------------------------------------------------------
# Web Search toolkit (Parallel.ai MCP)
# ---------------------------------------------------------------------------
_WEB_SEARCH_MCP_URL = "https://search.parallel.ai/mcp"

web_tools = MCPTools(
    url=_WEB_SEARCH_MCP_URL,
    transport="streamable-http",
)

# ---------------------------------------------------------------------------
# Composio toolkit (SaaS integrations: Gmail, Slack, GitHub, Notion, etc.)
# ---------------------------------------------------------------------------
_COMPOSIO_MCP_URL = "https://connect.composio.dev/mcp"
_COMPOSIO_API_KEY = getenv("COMPOSIO_API_KEY", "")

composio_tools = MCPTools(
    url=_COMPOSIO_MCP_URL,
    transport="streamable-http",
    server_params=StreamableHTTPClientParams(
        url=_COMPOSIO_MCP_URL,
        headers={"x-consumer-api-key": _COMPOSIO_API_KEY} if _COMPOSIO_API_KEY else None,
    ),
)

# ---------------------------------------------------------------------------
# E2B MCP (stdio - runs code in secure sandboxes)
# Requires: npm install -g @e2b/mcp-server (installed in Dockerfile)
# ---------------------------------------------------------------------------
e2b_tools = MCPTools(
    command="npx -y @e2b/mcp-server",
    transport="stdio",
    env={"E2B_API_KEY": getenv("E2B_API_KEY", "")} if getenv("E2B_API_KEY") else None,
)

# ---------------------------------------------------------------------------
# 1Password tools — wraps op CLI v2 with OP_SERVICE_ACCOUNT_TOKEN
# Requires: 1password-cli apt package (installed in Dockerfile)
#           OP_SERVICE_ACCOUNT_TOKEN env var set in Railway
# ---------------------------------------------------------------------------
def _op_env() -> dict:
    token = getenv("OP_SERVICE_ACCOUNT_TOKEN", "")
    return {**os.environ, "OP_SERVICE_ACCOUNT_TOKEN": token} if token else dict(os.environ)


def _op_run(*args: str, timeout: int = 15) -> str:
    import subprocess
    result = subprocess.run(
        ["op", *args],
        capture_output=True, text=True, env=_op_env(), timeout=timeout,
    )
    if result.returncode == 0:
        return result.stdout.strip() or "(success, no output)"
    return f"[op error] {result.stderr.strip()}"


@tool
def op_get_item(item: str, vault: str = "Main", field: str = "password") -> str:
    """Retrieve a field value from a 1Password item.

    Args:
        item: Item title or ID.
        vault: Vault name (default: Main).
        field: Field label to retrieve (default: password).
    """
    import json
    raw = _op_run("item", "get", item, "--vault", vault,
                  "--fields", f"label={field}", "--format", "json")
    if raw.startswith("[op error]"):
        return raw
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data[0].get("value", raw) if data else "(empty)"
        return data.get("value", raw)
    except Exception:
        return raw


@tool
def op_list_items(vault: str = "Main", category: str = "") -> str:
    """List items in a 1Password vault.

    Args:
        vault: Vault name (default: Main).
        category: Optional category filter (Login, Password, SecureNote, ApiCredentials…).
    """
    cmd = ["item", "list", "--vault", vault, "--format", "json"]
    if category:
        cmd += ["--categories", category]
    return _op_run(*cmd)


@tool
def op_create_item(title: str, password: str, vault: str = "Main",
                   category: str = "Password") -> str:
    """Create a new item in 1Password.

    Args:
        title: Item title.
        password: Password or secret value to store.
        vault: Vault name (default: Main).
        category: Item category (default: Password).
    """
    return _op_run("item", "create",
                   "--category", category,
                   "--title", title,
                   "--vault", vault,
                   f"password={password}")


@tool
def op_vault_list() -> str:
    """List all 1Password vaults accessible to the service account."""
    return _op_run("vault", "list", "--format", "json")


@tool
def op_generate_password(length: int = 20, symbols: bool = True) -> str:
    """Generate a secure random password using the op CLI.

    Args:
        length: Password length (default: 20).
        symbols: Include symbols (default: True).
    """
    cmd = ["generate-password", f"--length={length}"]
    if not symbols:
        cmd.append("--no-symbols")
    return _op_run(*cmd)


op_tools = [op_get_item, op_list_items, op_create_item, op_vault_list, op_generate_password]


# ---------------------------------------------------------------------------
# Sequential Thinking MCP (structured multi-step reasoning)
# ---------------------------------------------------------------------------
sequential_thinking_tools = MCPTools(
    command="npx -y @modelcontextprotocol/server-sequential-thinking",
    transport="stdio",
)


# ---------------------------------------------------------------------------
# Shell execution (runs commands on the server process)
# ---------------------------------------------------------------------------
@tool
def shell_execute(command: str, timeout: int = 60) -> str:
    """Run a shell command on the server and return stdout + stderr.

    Args:
        command: Shell command to execute (runs via /bin/sh -c).
        timeout: Maximum seconds to wait (default 60).
    """
    import subprocess

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        parts = []
        if out:
            parts.append(out)
        if err:
            parts.append(f"[stderr]\n{err}")
        if result.returncode != 0:
            parts.append(f"[exit code {result.returncode}]")
        return "\n".join(parts) if parts else "(no output)"
    except subprocess.TimeoutExpired:
        return f"[timed out after {timeout}s]"
    except Exception as exc:
        return f"[error] {exc}"


# ---------------------------------------------------------------------------
# Collection of all available toolkits
# ---------------------------------------------------------------------------
ALL_MCP_TOOLS = [web_tools, composio_tools, e2b_tools, sequential_thinking_tools, *op_tools, shell_execute]
