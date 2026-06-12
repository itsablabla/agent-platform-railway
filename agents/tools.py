"""
Shared MCP Toolkits
===================

All MCP-based toolkits in one place to avoid circular imports.

HTTP-based MCP servers:
- Web Search (Parallel.ai)  
- Composio (SaaS integrations)

stdio MCP servers (require binaries installed in Docker):
- E2B (code execution sandboxes)
- 1Password (credential management)
"""

from os import getenv

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
# 1Password MCP (stdio - credential management)
# Requires: 1password-cli package (installed in Dockerfile)
# ---------------------------------------------------------------------------
_1PASS_MCP_CMD = getenv("OP_MCP_COMMAND", "onepassword-mcp")
op_tools = MCPTools(
    command=_1PASS_MCP_CMD,
    transport="stdio",
)

# ---------------------------------------------------------------------------
# Collection of all available toolkits
# ---------------------------------------------------------------------------
ALL_MCP_TOOLS = [web_tools, composio_tools, e2b_tools, op_tools]
