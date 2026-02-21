from abc import ABC, abstractmethod

from app.models.message_payload import UserMessagePayload

class BaseCommand(ABC):
    command_name: str = ""
    command_aliases: list[str] = []

    @abstractmethod
    async def execute_command(self, payload: UserMessagePayload) -> None:
        pass
