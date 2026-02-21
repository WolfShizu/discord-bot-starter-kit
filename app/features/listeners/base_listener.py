from abc import ABC, abstractmethod

from app.models.message_payload import UserMessagePayload
from app.features.listeners.enums import ListenerEventType

class BaseListener(ABC):
    listener_name: str = ""
    listener_type: ListenerEventType

    @abstractmethod
    async def handle_event(self, payload: UserMessagePayload) -> None:
        pass
