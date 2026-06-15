"""
Telegram Interface
==================
Receives bot updates via webhook and routes them to an agno Agent/Team.

Required env vars:
  TELEGRAM_BOT_TOKEN       — bot token from @BotFather
  TELEGRAM_WEBHOOK_SECRET  — optional secret for X-Telegram-Bot-Api-Secret-Token validation

After deploying, call Telegram.register_webhook(url) once to tell Telegram
where to send updates, e.g.:
  await interface.register_webhook("https://your-domain.com/telegram/webhook")
"""

from __future__ import annotations

import os
from typing import List, Optional, Union

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from agno.agent import Agent, RemoteAgent
from agno.team import RemoteTeam, Team
from agno.utils.log import log_error, log_info

_TG_API = "https://api.telegram.org/bot{token}/{method}"


def _tg(token: str, method: str, **kwargs) -> dict:
    url = _TG_API.format(token=token, method=method)
    try:
        r = httpx.post(url, json=kwargs, timeout=None)
        return r.json()
    except Exception as exc:
        log_error(f"Telegram API error ({method}): {exc}")
        return {}


def _split(text: str, limit: int = 4096) -> List[str]:
    return [text[i : i + limit] for i in range(0, len(text), limit)]


class Telegram:
    type = "telegram"

    def __init__(
        self,
        agent: Optional[Union[Agent, RemoteAgent]] = None,
        team: Optional[Union[Team, RemoteTeam]] = None,
        prefix: str = "/telegram",
        tags: Optional[List[str]] = None,
    ):
        if not (agent or team):
            raise ValueError("Telegram interface requires an agent or team")
        self.agent = agent
        self.team = team
        self.prefix = prefix
        self.tags = tags or ["Telegram"]
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

    async def register_webhook(self, webhook_url: str) -> dict:
        """Register webhook URL with Telegram. Call once after startup."""
        params: dict = {"url": webhook_url, "allowed_updates": ["message", "callback_query"]}
        if self.secret:
            params["secret_token"] = self.secret
        return _tg(self.bot_token, "setWebhook", **params)

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix=self.prefix, tags=self.tags)
        bot_token = self.bot_token
        secret = self.secret
        agent = self.agent
        team = self.team

        @router.get("/status", operation_id="telegram_status", summary="Telegram interface health")
        async def telegram_status():
            active = bool(bot_token)
            return {"status": "active" if active else "no_token", "token_set": active}

        @router.post(
            "/webhook",
            operation_id="telegram_webhook",
            summary="Receive Telegram bot updates",
            status_code=200,
        )
        async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
            if secret:
                incoming = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
                if incoming != secret:
                    raise HTTPException(status_code=403, detail="Invalid secret token")

            update = await request.json()
            background_tasks.add_task(_handle_update, update, agent, team, bot_token)
            return {"ok": True}

        async def _handle_update(update: dict, agent, team, bot_token: str):
            message = update.get("message") or update.get("edited_message")
            if not message:
                return

            chat_id = message.get("chat", {}).get("id")
            user_id = str(message.get("from", {}).get("id", ""))
            text = message.get("text") or message.get("caption", "")
            session_id = str(chat_id)

            if not text or not chat_id:
                return

            try:
                if agent:
                    response = await agent.arun(text, user_id=user_id, session_id=session_id)
                else:
                    response = await team.arun(text, user_id=user_id, session_id=session_id)

                reply = response.content if response else "I couldn't generate a response."
                for chunk in _split(reply or ""):
                    _tg(bot_token, "sendMessage", chat_id=chat_id, text=chunk, parse_mode="Markdown")
            except Exception as exc:
                log_error(f"Telegram handler error: {exc}")
                _tg(bot_token, "sendMessage", chat_id=chat_id,
                    text="Sorry, there was an error processing your message.")

        return router
