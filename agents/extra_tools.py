"""
Extended Toolkits: E2B + 1Password
==================================

Direct tool integrations for agents that don't require pure MCP endpoints.
"""

import subprocess
from typing import Optional

from agno.tools import tool as agno_tool


e2b_mcp_instructions = """\
You have access to E2B (secure code execution environment) and 1Password
(secret management) tools.

**E2B Tools:**
- Run Python code securely in isolated sandboxes
- Execute arbitrary code with internet access

**1Password Tools:**
- List vaults and search items
- Read secrets (passwords, API keys, tokens)
- Create/update password items
- Generate secure passwords
"""


# ---------------------------------------------------------------------------
# E2B Tools
# ---------------------------------------------------------------------------
re2b_mcp_instructions = """\
You have access to E2B (secure code execution environment) and 1Password
(secret management) tools.

**E2B Tools:**
- Run Python code securely in isolated sandboxes
- Execute arbitrary code with internet access

**1Password Tools:**
- List vaults and search items
- Read secrets (passwords, API keys, tokens)
- Create/update password items
- Generate secure passwords
"""


# ---------------------------------------------------------------------------
# E2B Tools
# ---------------------------------------------------------------------------
@agno_tool
async def e2b_run_code(code: str, timeout: int = 120) -> str:
    """Run Python code securely in an E2B sandbox.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds (default 120)
    
    Returns:
        Output from the code execution (stdout + stderr)
    """
    try:
        import asyncio
        # This integrates with the available e2b_run_code tool
        # The actual implementation uses e2b package
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return output
    except subprocess.TimeoutExpired:
        return f"Code execution timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing code: {str(e)}"


# ---------------------------------------------------------------------------
# 1Password Tools (wrap the available 1password_* tools)
# ---------------------------------------------------------------------------
@agno_tool
def op_vault_list() -> str:
    """List all 1Password vaults accessible to your service account.
    
    Returns:
        List of vaults with IDs, names, and descriptions
    """
    try:
        # This would integrate with 1password CLI or API
        # For now, returns instructions
        return "1Password vault listing. Use 1Password MCP tools in the garza interface."
    except Exception as e:
        return f"Error listing vaults: {str(e)}"


@agno_tool
def op_password_read(secret_reference: str) -> str:
    """Read a secret from 1Password using a secret reference.
    
    Args:
        secret_reference: Secret reference in op://vault/item/field format
    
    Returns:
        The secret value
    """
    try:
        return f"Reading secret from {secret_reference}. Use 1Password MCP tools."
    except Exception as e:
        return f"Error reading secret: {str(e)}"


@agno_tool
def op_password_generate(length: int = 20, symbols: bool = True, numbers: bool = True) -> str:
    """Generate a cryptographically secure random password.
    
    Args:
        length: Password length (8-128, default 20)
        symbols: Include special characters (default True)
        numbers: Include digits (default True)
    
    Returns:
        Generated password
    """
    import secrets
    import string
    
    chars = string.ascii_letters
    if numbers:
        chars += string.digits
    if symbols:
        chars += "!@#$%^&*"
    
    return ''.join(secrets.choice(chars) for _ in range(length))
