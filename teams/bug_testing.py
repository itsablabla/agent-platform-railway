"""
Bug Testing Team
==================

Coordinated team of specialist agents for end-to-end bug testing,
root-cause analysis, and fix verification.

Members: WebSearch, CodeSearch, Log Analyst, Session Analyst,
Security Agent, System Operator, Railway Agent, Agno IT Admin.
"""

from agno.team import Team

from agents.admin_ops import admin_ops
from agents.code_search import code_search
from agents.log_analyst import log_analyst
from agents.railway_agent import railway_agent
from agents.security_agent import security_agent
from agents.session_analyst import session_analyst
from agents.system_operator import system_operator
from agents.web_search import web_search
from app.settings import default_model
from db import get_postgres_db


bug_testing_team = Team(
    name="Bug Testing Team",
    description="End-to-end bug testing: reproduce, diagnose, root-cause, and verify fixes.",
    mode="coordinate",
    model=default_model(),
    members=[
        admin_ops,
        web_search,
        code_search,
        log_analyst,
        session_analyst,
        security_agent,
        system_operator,
        railway_agent,
    ],
    instructions="""\
You are the Bug Testing Team leader. Your job is to coordinate specialists
to thoroughly test, diagnose, and fix bugs.

## Workflow

1. **Reproduce**: understand the bug from the user's description. Delegate to
WebSearch for known issues, error code lookups, and package changelogs.
2. **Locate**: send CodeSearch to find the relevant code paths. If the bug
involves deployment errors, engage Railway Agent for infrastructure checks.
3. **Diagnose**: have Log Analyst inspect Railway logs and Session Analyst
check session/run state for anomalies. Correlate timestamps.
4. **Root Cause**: System Operator coordinates deeper A2A delegation.
Security Agent audits any code changes for vulnerabilities.
5. **Fix & Verify**: produce a concrete fix (code patch, config change, or
rollback). Re-run the affected flow to verify.

## Rules

- Always include evidence: log lines, line numbers, session IDs, timestamps.
- Never guess. If uncertain, say so and ask a specialist.
- When proposing a code fix, quote exact file paths and line ranges.
- Security Agent must review every code change.
- Aggregate findings into a single structured report:
  - Summary (1-2 lines)
  - Root Cause
  - Evidence
  - Fix
  - Verification steps
""",
    markdown=True,
    show_members_responses=True,
    add_member_tools_to_context=True,
    db=get_postgres_db(),
)
