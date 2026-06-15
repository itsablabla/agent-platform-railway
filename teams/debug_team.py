"""
Debug Team
====

Created from code so it inherits default_model() = moonshotai/kimi-k2.6.
Replaces the Studio-created version that had amazon/nova-pro-v1.
"""

from agno.team import Team, TeamMode

from agents.admin_ops import admin_ops
from agents.claude_opus import claude_opus_agent
from agents.code_search import code_search
from agents.composio import composio_agent
from agents.e2b_coder import e2b_coder
from agents.gpt_55 import gpt55_agent
from agents.jada import jada
from agents.kimi import kimi_agent
from agents.log_analyst import log_analyst
from agents.openrouter import openrouter_agent
from agents.railway_agent import railway_agent
from agents.security_agent import security_agent
from agents.session_analyst import session_analyst
from agents.system_operator import system_operator
from agents.web_search import web_search
from app.settings import default_model
from db import get_postgres_db
from teams.bug_testing import bug_testing_team


debug_team = Team(
    id="debug",
    name="Debug",
    description="Full team with all agents for general debugging and development.",
    mode=TeamMode.coordinate,
    model=default_model(),
    members=[
        admin_ops,
        claude_opus_agent,
        code_search,
        composio_agent,
        e2b_coder,
        gpt55_agent,
        jada,
        kimi_agent,
        log_analyst,
        openrouter_agent,
        railway_agent,
        security_agent,
        session_analyst,
        system_operator,
        web_search,
        bug_testing_team,
    ],
    instructions="You have access to every agent. Delegate tasks to the most appropriate specialist.",
    markdown=True,
    show_members_responses=True,
    db=get_postgres_db(),
)
