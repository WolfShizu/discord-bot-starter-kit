from dataclasses import dataclass
from typing import Optional, Any, Callable, Awaitable

from discord import Message, TextChannel, Embed

@dataclass
class BotResponsePayload:
    content: str
    embed: Optional[Embed] = None

@dataclass
class UserMessagePayload:
    message: Message
    send_message_function: Callable[[BotResponsePayload], Awaitable[Any]]

    raw_message: Optional[str] = None
    is_command: Optional[bool] = None
    command_name: Optional[str] = None
    arguments: Optional[list[str]] = None