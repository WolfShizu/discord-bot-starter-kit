# TODO Criar uma função pra exibir os dados. Essa função deve ser capaz de lidar com os seguintes dados:
# - Local do erro (feature, comando, listener, etc)
# - Nome da feature/serviço, caso ele tenha um nome

from types import TracebackType
import traceback as tb_module

from app.core.exceptions.global_exception import GlobalException

from app.core.types import ExceptionSeverity

from app.core.telemetry import TelemetryExceptionPayload

class ExceptionHandler:
    def __init__(self):
        self.fail_map = {
            ExceptionSeverity.LOW: "LEVE",
            ExceptionSeverity.MEDIUM: "MÉDIA",
            ExceptionSeverity.CRITICAL: "ALTA"
        }

    async def handle_exception(
            self,
            discord_event: str,
            event_arguments: tuple,
            exception: BaseException | None,
            traceback: TracebackType | None
    ):
        if exception is None:
            return

        if isinstance(exception, GlobalException):
            severity = exception.severity
            message = exception.message

        else:
            severity = ExceptionSeverity.UNKNOWN
            message = str(exception)

        name = type(exception).__name__

        trimmed_traceback_lines = tb_module.format_exception(type(exception), exception, traceback, limit= 2)
        trimmed_traceback_string = "".join(trimmed_traceback_lines)

        full_traceback_lines = tb_module.format_exception(type(exception), exception, traceback, limit= 2)
        full_traceback_string = "".join(full_traceback_lines)

        return TelemetryExceptionPayload(
            severity= severity,
            name= name,
            message= message,
            discord_event= discord_event,
            arguments= event_arguments,
            trimmed_traceback= trimmed_traceback_string,
            full_traceback= full_traceback_string
        )

    async def handle_feature_exception(self, exception: BaseException, feature_name: str):
        if exception is None:
            return

        if isinstance(exception, GlobalException):
            if exception.severity == ExceptionSeverity.CRITICAL:
                raise exception
        else:
            # TODO Melhorar tratamento de erro
            print(f"Erro desconhecido na feature {feature_name}: {type(exception).__name__}")
            print(f"Detalhes: {exception}")
