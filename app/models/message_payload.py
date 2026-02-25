from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from discord import Message, Embed

@dataclass
class BotResponsePayload:
    content: str
    embed: Embed | None = None
    reply_to: int | None = None

@dataclass
class UserMessagePayload:
    message: Message
    send_message_function: Callable[[BotResponsePayload], Awaitable[Any]]

    message_id: int
    author_id: int
    guild_id: int | None

    raw_message: str | None = None

    is_private_message: bool | None = None

    is_command: bool | None = None
    command_name: str | None = None
    arguments: list[str] | None = None

    is_admin_role: bool | None = None
    is_authorized_role: bool | None = None
    is_authorized_user: bool | None = None
