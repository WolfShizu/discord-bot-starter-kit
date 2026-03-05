# TODO Criar uma função pra exibir os dados. Essa função deve ser capaz de lidar com os seguintes dados:
# - Local do erro (feature, comando, listener, etc)
# - Nome da feature/serviço, caso ele tenha um nome

from types import TracebackType
import traceback as tb_module

from app.core.exceptions.global_exception import GlobalException

from app.core.types import ExceptionSeverity

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

        print("=" * 30)

        if isinstance(exception, GlobalException):
            severity_label = self.fail_map.get(exception.severity, "DESCONHECIDO")
            print(f"FALHA {severity_label}")
            print(f"Falha: {exception.message}")
        else:
            print(f"FALHA DESCONHECIDA: {type(exception).__name__}")
            print(f"Detalhes: {exception}")

        print(f"Evento: {discord_event}")
        print(f"Argumentos recebidos pelo evento: {event_arguments}")
        print("--- TRACEBACK DO ERRO ---")
        tb_module.print_exception(type(exception), exception, traceback)
        print("-------------------------")

        print("=" * 30)

    async def handle_feature_exception(self, exception: BaseException, feature_name: str):
        if exception is None:
            return

        if isinstance(exception, GlobalException):
            if exception.severity == ExceptionSeverity.CRITICAL:
                raise exception
        else:
            print(f"Erro desconhecido na feature {feature_name}: {type(exception).__name__}")
            print(f"Detalhes: {exception}")
