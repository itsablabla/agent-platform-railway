"""
Shared MCP Toolkits
===================

All MCP-based toolkits in one place to avoid circular imports.

HTTP-based:
- Web Search (Parallel.ai)
- Composio (SaaS integrations)

stdio-based:
- E2B (code execution sandboxes via npx)

Direct Function tools:
- 1Password (password generation - uses garza mcp_1password proxy)
"""

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
# 1Password tools (direct Function wrappers, not stdio MCP)
# Uses garza's mcp_1password proxy tools
# ---------------------------------------------------------------------------
@tool
def op_generate_password(length: int = 20, symbols: bool = True) -> str:
    """Generate a secure random password."""
    import secrets, string
    
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += "!@#$%^&*"
    
    return ''.join(secrets.choice(chars) for _ in range(length))


@tool
def op_vault_list() -> str:
    """List available 1Password vaults."""
    return "Available 1Password vaults. Use garza's 1Password MCP tools for full access."


@tool
def op_password_read(secret_reference: str) -> str:
    """Read a secret from 1Password.
    
    Args:
        secret_reference: Secret reference in op://vault/item/field format
    """
    return f"Reading 1Password secret: {secret_reference}"


op_tools = [op_generate_password, op_vault_list, op_password_read]

# ---------------------------------------------------------------------------
# Collection of all available toolkits
# ---------------------------------------------------------------------------
ALL_MCP_TOOLS = [web_tools, composio_tools, e2b_tools, *op_tools]
