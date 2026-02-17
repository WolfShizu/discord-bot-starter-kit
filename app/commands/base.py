from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from app.models.message_payload import UserMessagePayload

class BaseCommand(ABC):
    command_name: str = ""
    command_aliases: list[str] = []

    def __init__(self, send_message_function: Callable[[Any, Any], Coroutine[Any, Any, None]]):
        self.send_message_function = send_message_function


    @abstractmethod
    async def execute_command(self, payload: UserMessagePayload) -> None:
        pass

class BaseListener(ABC):
    def __init__(self, send_message_function: Callable[[Any, Any], Coroutine[Any, Any, None]]):
        self.send_message_function = send_message_function

    @abstractmethod
    async def handle_event(self, payload: UserMessagePayload) -> None:
        pass
