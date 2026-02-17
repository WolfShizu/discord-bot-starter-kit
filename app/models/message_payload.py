from dataclasses import dataclass
from typing import Optional, Any, Callable, Awaitable

from discord import Message, Embed

@dataclass
class BotResponsePayload:
    content: str
    embed: Optional[Embed] = None
    reply_author = None # TODO Finalizar implementação

@dataclass
class UserMessagePayload:
    message: Message
    send_message_function: Callable[[BotResponsePayload], Awaitable[Any]]

    is_private_message: Optional[bool] = None

    raw_message: Optional[str] = None
    is_command: Optional[bool] = None
    command_name: Optional[str] = None
    arguments: Optional[list[str]] = None

    is_admin_role: Optional[bool] = None
    is_authorized_role: Optional[bool] = None
    is_authorized_user: Optional[bool] = None
