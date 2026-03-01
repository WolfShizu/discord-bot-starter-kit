from app.core.types import ExceptionSeverity

class BaseException(Exception):
    def __init__(
            self,
            message: str,
            severity: ExceptionSeverity
    ):
        self.message = message
        self.severity = severity
        super().__init__(self.message)
