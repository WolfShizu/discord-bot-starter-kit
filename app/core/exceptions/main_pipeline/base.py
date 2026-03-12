from app.core.exceptions.global_exception import GlobalException

from app.core.types import ExceptionSeverity

class MainPipelineBaseException(GlobalException):
    def __init__(
            self,
            message: str,
            severity: ExceptionSeverity = ExceptionSeverity.CRITICAL
    ):

        super().__init__(message, severity)
