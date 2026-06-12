"""
Shared MCP Toolkits
===================

All MCP-based toolkits in one place to avoid circular imports.

HTTP-based MCP servers (available immediately):
- Web Search (Parallel.ai)
- Composio (SaaS integrations)

NOTE: stdio MCP servers (E2B, 1Password) can be added when their binaries
are installed in the Railway environment. See the MCP transport docs.
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
# Collection of available toolkits
# ---------------------------------------------------------------------------
ALL_MCP_TOOLS = [web_tools, composio_tools]
