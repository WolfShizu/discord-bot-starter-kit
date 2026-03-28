from app.core.exceptions.main_pipeline.base import MainPipelineBaseException

from app.core.types import ExceptionSeverity

class MessageHandlerException(MainPipelineBaseException):
    def __init__(
            self,
            message: str,
            severity: ExceptionSeverity = ExceptionSeverity.MEDIUM
    ):

        super().__init__(message, severity)

class UnableToSendMessage(MessageHandlerException):
    pass

class UnableToGetChannelId(MessageHandlerException):
    pass
