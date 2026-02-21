from abc import ABC, abstractmethod

from app.models.message_payload import UserMessagePayload

class BaseListener(ABC):
    listener_name: str = ""

    @abstractmethod
    async def handle_event(self, payload: UserMessagePayload) -> None:
        pass
