from app.core.exceptions.main_pipeline.base import MainPipelineBaseException

from app.core.types import ExceptionSeverity

class FeatureRgistrationException(MainPipelineBaseException):
    def __init__(
            self,
            message: str,
            severity: ExceptionSeverity = ExceptionSeverity.LOW
    ):

        super().__init__(message, severity)

class MissingFeatureNameError(FeatureRgistrationException):
    pass

class DuplicateFeatureNameError(FeatureRgistrationException):
    pass

class WrongTypeFeatureError(FeatureRgistrationException):
    pass
