"""
Discord Interface
=================
Receives Discord interactions (slash commands, messages) and routes them to
an agno Agent/Team.

Required env vars:
  DISCORD_PUBLIC_KEY   — Ed25519 public key from Discord Developer Portal
  DISCORD_BOT_TOKEN    — bot token for sending followup messages
  DISCORD_APP_ID       — application ID (for interaction followups)

Discord requires synchronous Ed25519 signature verification on every request.
Responses use a deferred model: return type=5 immediately, then PATCH the
followup endpoint once the agent run completes.
"""

from __future__ import annotations

import json
import os
from typing import List, Optional, Union

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from agno.agent import Agent, RemoteAgent
from agno.team import RemoteTeam, Team
from agno.utils.log import log_error, log_info

_DISCORD_API = "https://discord.com/api/v10"

# Interaction types
_PING = 1
_APPLICATION_COMMAND = 2
_MESSAGE_COMPONENT = 3

# Response types
_PONG = 1
_CHANNEL_MESSAGE_WITH_SOURCE = 4
_DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5


def _parse_pubkey(hex_key: str) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(bytes.fromhex(hex_key))


def _verify(public_key: Ed25519PublicKey, signature: str, timestamp: str, body: bytes) -> bool:
    try:
        public_key.verify(bytes.fromhex(signature), timestamp.encode() + body)
        return True
    except InvalidSignature:
        return False


def _discord_headers(bot_token: str) -> dict:
    return {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}


def _send_followup(app_id: str, interaction_token: str, content: str, bot_token: str):
    url = f"{_DISCORD_API}/webhooks/{app_id}/{interaction_token}"
    for i, chunk in enumerate([content[i:i+2000] for i in range(0, len(content), 2000)]):
        try:
            if i == 0:
                httpx.patch(
                    f"{_DISCORD_API}/webhooks/{app_id}/{interaction_token}/messages/@original",
                    headers=_discord_headers(bot_token),
                    json={"content": chunk},
                    timeout=None,
                )
            else:
                httpx.post(url, headers=_discord_headers(bot_token),
                           json={"content": chunk}, timeout=None)
        except Exception as exc:
            log_error(f"Discord followup error: {exc}")


class Discord:
    type = "discord"
    version = "1"

    def __init__(
        self,
        agent: Optional[Union[Agent, RemoteAgent]] = None,
        team: Optional[Union[Team, RemoteTeam]] = None,
        prefix: str = "/discord",
        tags: Optional[List[str]] = None,
    ):
        if not (agent or team):
            raise ValueError("Discord interface requires an agent or team")
        self.agent = agent
        self.team = team
        self.prefix = prefix
        self.tags = tags or ["Discord"]
        self.public_key_hex = os.getenv("DISCORD_PUBLIC_KEY", "")
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN", "")
        self.app_id = os.getenv("DISCORD_APP_ID", "")

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix=self.prefix, tags=self.tags)
        public_key_hex = self.public_key_hex
        bot_token = self.bot_token
        app_id = self.app_id
        agent = self.agent
        team = self.team

        pubkey: Optional[Ed25519PublicKey] = None
        if public_key_hex:
            try:
                pubkey = _parse_pubkey(public_key_hex)
            except Exception as exc:
                log_error(f"Discord: invalid DISCORD_PUBLIC_KEY — {exc}")

        @router.get("/status", operation_id="discord_status", summary="Discord interface health")
        async def discord_status():
            active = bool(public_key_hex and bot_token)
            return {
                "status": "active" if active else "missing_config",
                "public_key_set": bool(public_key_hex),
                "bot_token_set": bool(bot_token),
                "app_id_set": bool(app_id),
            }

        @router.post(
            "/interactions",
            operation_id="discord_interactions",
            summary="Receive Discord interactions",
            status_code=200,
        )
        async def discord_interactions(request: Request, background_tasks: BackgroundTasks):
            signature = request.headers.get("X-Signature-Ed25519", "")
            timestamp = request.headers.get("X-Signature-Timestamp", "")
            body = await request.body()

            if pubkey:
                if not signature or not timestamp:
                    raise HTTPException(status_code=401, detail="Missing Discord signature headers")
                if not _verify(pubkey, signature, timestamp, body):
                    raise HTTPException(status_code=401, detail="Invalid Discord signature")

            interaction = json.loads(body)
            itype = interaction.get("type")

            if itype == _PING:
                return {"type": _PONG}

            if itype in (_APPLICATION_COMMAND, _MESSAGE_COMPONENT):
                background_tasks.add_task(
                    _handle_interaction, interaction, agent, team, bot_token, app_id
                )
                return {"type": _DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE}

            return {"type": _CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": "Unsupported interaction type."}}

        async def _handle_interaction(interaction: dict, agent, team, bot_token: str, app_id: str):
            interaction_token = interaction.get("token", "")
            data = interaction.get("data", {})
            user = (interaction.get("member", {}).get("user") or interaction.get("user") or {})
            user_id = str(user.get("id", ""))
            guild_id = interaction.get("guild_id", "")
            session_id = guild_id or user_id

            # Slash command: options list → reconstruct message
            options = data.get("options", [])
            if options:
                text = " ".join(
                    str(opt.get("value", "")) for opt in options if opt.get("value") is not None
                )
            else:
                text = data.get("name", "")

            if not text:
                _send_followup(app_id, interaction_token,
                               "Please provide a message.", bot_token)
                return

            try:
                if agent:
                    response = await agent.arun(text, user_id=user_id, session_id=session_id)
                else:
                    response = await team.arun(text, user_id=user_id, session_id=session_id)

                reply = (response.content if response else None) or "No response generated."
                _send_followup(app_id, interaction_token, reply, bot_token)
            except Exception as exc:
                log_error(f"Discord handler error: {exc}")
                _send_followup(app_id, interaction_token,
                               "Sorry, there was an error processing your request.", bot_token)

        return router
