"""
Shared MCP Toolkits
===================

Initialises all MCP-based toolkits in one place to avoid circular imports
between agent files.
"""

from os import getenv

from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams

# ---------------------------------------------------------------------------
# Web Search toolkit (Parallel.ai MCP or keyless fallback)
# ---------------------------------------------------------------------------
_WEB_SEARCH_MCP_URL = "https://search.parallel.ai/mcp"

web_tools = MCPTools(
    url=_WEB_SEARCH_MCP_URL,
    transport="streamable-http",
)

# ---------------------------------------------------------------------------
# Composio toolkit (SaaS integrations: Gmail, Slack, GitHub, Notion, …)
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
