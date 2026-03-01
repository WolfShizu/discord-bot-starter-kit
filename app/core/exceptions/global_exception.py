from app.core.types import ExceptionSeverity

class GlobalException(Exception):
    def __init__(
            self,
            message: str,
            severity: ExceptionSeverity
    ):
        self.message = message
        self.severity = severity
        super().__init__(self.message)
