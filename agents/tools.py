"""
Shared MCP Toolkits
===================

All MCP-based toolkits in one place to avoid circular imports.

Note: stdio MCP servers (E2B, 1Password) require their binaries to be
installed in the environment. The fallback is graceful — if the binary is
not found, the tools simply won’t be available.
"""

from os import getenv

from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams
from agno.utils.log import log_warning

# ---------------------------------------------------------------------------
# Web Search toolkit (Parallel.ai MCP)
# ---------------------------------------------------------------------------
_WEB_SEARCH_MCP_URL = "https://search.parallel.ai/mcp"

web_tools = MCPTools(
    url=_WEB_SEARCH_MCP_URL,
    transport="streamable-http",
)

# ---------------------------------------------------------------------------
# Composio toolkit (SaaS integrations)
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
# E2B MCP (stdio - runs MCP servers inside E2B sandboxes)
# Requires: npm install -g @e2b/mcp-server  (or npx)
# ---------------------------------------------------------------------------
try:
    e2b_tools = MCPTools(
        command="npx -y @e2b/mcp-server",
        transport="stdio",
    )
except Exception:
    log_warning("E2B MCP server not available. Install with: npm install -g @e2b/mcp-server")
    e2b_tools = None

# ---------------------------------------------------------------------------
# 1Password MCP (stdio - local 1Password MCP binary)
# Requires: 1Password CLI + onepassword-mcp binary
# Linux: download from 1Password dev docs
# ---------------------------------------------------------------------------
try:
    _OP_MCP_CMD = getenv("OP_MCP_COMMAND", "onepassword-mcp")
    op_tools = MCPTools(
        command=_OP_MCP_CMD,
        transport="stdio",
    )
except Exception:
    log_warning("1Password MCP server not available. Install the 1Password MCP binary.")
    op_tools = None

# ---------------------------------------------------------------------------
# Collect available toolkits for easy importing
# ---------------------------------------------------------------------------
ALL_MCP_TOOLS = [web_tools, composio_tools]
if e2b_tools:
    ALL_MCP_TOOLS.append(e2b_tools)
if op_tools:
    ALL_MCP_TOOLS.append(op_tools)
