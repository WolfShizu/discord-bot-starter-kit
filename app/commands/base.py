from abc import ABC, abstractmethod

from app.models.message_payload import UserMessagePayload

class BaseCommand(ABC):
    def __init__(self):
        self.name: str = ""
        self.aliases: list[str] = []

    @abstractmethod
    async def execute(self, payload: UserMessagePayload) -> None:
        pass
    
class BaseListener(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def handle_event(self, payload: UserMessagePayload) -> None:
        pass