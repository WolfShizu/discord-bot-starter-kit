from typing import Any

import sys

from types import TracebackType
import traceback as tb_module

from app.core.exceptions.global_exception import GlobalException

from app.core.types import ExceptionSeverity

from app.core.telemetry import TelemetryExceptionPayload, Telemetry

class ExceptionHandler:
    def __init__(self, telemetry: Telemetry):
        self.telemetry = telemetry

        self.fail_map = {
            ExceptionSeverity.LOW: "LEVE",
            ExceptionSeverity.MEDIUM: "MÉDIA",
            ExceptionSeverity.CRITICAL: "ALTA"
        }

    async def handle_default_exception(
            self,
            exception: BaseException | None,
            traceback: TracebackType | None = None,
            error_message: str | None = None,
            extra_data: dict[str, Any] | None = None
        ) -> None:
        """Trata qualquer tipo de exceção no código

        Args:
            exception: Exceção. Pode ser base ou customizada
            traceback: Caso esteja disponível. Opcional. O traceback é gerado na função
            error_message: Mensagem customizada para o erro, caso ele já tenha sido tratado. Com isso, a mensagem dentro da exceção é ignorada
            extra_data: Dados extras para a exceção. Apenas dados pré-definidos são exibidos no dashboard (como os do discord). O resto apenas vai aos logs
        """
        if exception is None:
            return

        if isinstance(exception, GlobalException):
            severity = exception.severity
            message = exception.message

        else:
            severity = ExceptionSeverity.UNKNOWN
            message = str(exception)

        if error_message:
            message = error_message

        if not traceback:
            traceback = exception.__traceback__

        exception_type = type(exception).__name__

        trimmed_traceback_lines = tb_module.format_exception(type(exception), exception, traceback, limit= 2)
        trimmed_traceback_string = "".join(trimmed_traceback_lines)

        full_traceback_lines = tb_module.format_exception(type(exception), exception, traceback, limit= 2)
        full_traceback_string = "".join(full_traceback_lines)

        telemetry_data = TelemetryExceptionPayload(
            severity= severity,
            type= exception_type,
            message= message,
            trimmed_traceback= trimmed_traceback_string,
            full_traceback= full_traceback_string,
            extra_data= extra_data if extra_data else {}
        )

        await self.telemetry.record_exception(telemetry_data)

        if severity == ExceptionSeverity.CRITICAL:
            sys.exit()

    async def handle_discord_exception(
            self,
            discord_event: str,
            event_arguments: tuple[Any],
            exception: BaseException | None,
            traceback: TracebackType | None
    ) -> None:
        """Trata a exceção capturada pelo discord"""
        if exception is None:
            return

        await self.handle_default_exception(
            exception= exception,
            traceback= traceback,
            extra_data= {
                "discord_data": {
                    "discord_event": discord_event,
                    "event_arguments": event_arguments
                }
            }
        )

    async def handle_feature_exception(
            self,
            exception: BaseException,
            feature_name: str
        ) -> None:
        if exception is None:
            return

        await self.handle_default_exception(
            exception= exception,
            error_message= (
                f"Falha na feature {feature_name}. Classe: {type(exception).__name__}\n"
                f"Detalhes: {str(exception)}"
            ),
            extra_data= {
                "feature_name": feature_name
            }
        )
