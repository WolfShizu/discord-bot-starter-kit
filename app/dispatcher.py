# TODO Configurar o event type do listener
# TODO Configurar o listener type do Listener, para definir se ele deve vir antes ou depois de comandos, ou se ele não deve ser chamado caso um comando seja executado

from typing import Any, Type, cast
import time

from dataclasses import dataclass

from app.features.commands.base_command import BaseCommand
from app.features.listeners.base_listener import BaseListener

from app.features.listeners.enums import ListenerEventType

from app.models.message_payload import UserMessagePayload

from app.core.telemetry import Telemetry, TelemetryFeaturePayload, TelemetryBatchFeaturePayload
from app.core.types import FeatureType

# Exceções
from app.core.exceptions.exception_handler import ExceptionHandler
from app.core.exceptions.main_pipeline.dispatcher_exceptions import (
    MissingFeatureNameError,
    DuplicateFeatureNameError,
    WrongTypeFeatureError
)

@dataclass
class FeatureExecutionResult:
    telemetry: TelemetryFeaturePayload
    exception: Exception | None

class Dispatcher:
    """
    Classe responsável por enviar os payloads para as funções, além de registrá-los
    """
    def __init__(self, exception_handler: ExceptionHandler):
        self.exception_handler = exception_handler
        self.commands_map: dict[str, BaseCommand] = {}
        self.listener_map: dict[ListenerEventType, list[BaseListener]] = {event_type: [] for event_type in ListenerEventType}
        self.registered_names = set()

        self.telemetry = Telemetry()

    async def dispatch_message(self, message_payload: UserMessagePayload):
        telemetry_batch = TelemetryBatchFeaturePayload(
            user_id= message_payload.author_id,
            guild_id= message_payload.guild_id,
            message_id= message_payload.message_id,
        )
        start_time = time.perf_counter()
        # Passa a mensagem para os listeners
        for listener in self.listener_map[ListenerEventType.MESSAGE]:
            listener_result = await self._execute_listener(
                listener= listener,
                payload= message_payload
            )

            telemetry_batch.features_executed.append(listener_result.telemetry)

            if listener_result.exception:
                await self.exception_handler.handle_feature_exception(
                    exception= listener_result.exception,
                    feature_name= listener.listener_name
                )

        # Executa o comando, se houver
        if message_payload.is_command and isinstance(message_payload.command_name, str):
            command = self.commands_map.get(message_payload.command_name.lower())

            if command:
                command_result = await self._execute_command(
                    command= command,
                    payload= message_payload
                )
                telemetry_batch.features_executed.append(command_result.telemetry)

                if command_result.exception:
                    await self.exception_handler.handle_feature_exception(
                        exception= command_result.exception,
                        feature_name= command.command_name
                    )

        duration = (time.perf_counter() - start_time) * 1000
        telemetry_batch.total_execution_time = duration
        await self.telemetry.record_batch(telemetry_batch)

    async def _execute_command(self, command: BaseCommand, payload: UserMessagePayload):
        start_time = time.perf_counter()
        sucess = False
        error_type = None
        exception = None

        try:
            await command.execute_command(payload)
            sucess = True

        except Exception as error:
            error_type = type(error).__name__
            exception = error


        duration = (time.perf_counter() - start_time) * 1000

        telemetry_data = TelemetryFeaturePayload(
            feature_type= FeatureType.COMMAND,
            feature_name= command.command_name,
            execution_time= duration,
            success= sucess,
            user_id= payload.author_id,
            guild_id= payload.guild_id,
            error_type = error_type
        )

        result_payload = FeatureExecutionResult(
            telemetry= telemetry_data,
            exception= exception
        )

        return result_payload

    async def _execute_listener(self, listener: BaseListener, payload: UserMessagePayload):
        start_time = time.perf_counter()
        sucess = False
        error_type = None
        exception = None

        try:
            await listener.handle_event(payload)
            sucess = True

        except Exception as error:
            error_type = type(error).__name__
            exception = error

        duration = (time.perf_counter() - start_time) * 1000

        telemetry_data = TelemetryFeaturePayload(
            feature_type= FeatureType.LISTENER,
            feature_name= listener.listener_name,
            execution_time= duration,
            success= sucess,
            user_id= payload.author_id,
            guild_id= payload.guild_id,
            error_type = error_type
        )

        result_payload = FeatureExecutionResult(
            telemetry= telemetry_data,
            exception= exception
        )

        return result_payload

    def register_command(self, command_classe: Type[BaseCommand]):
        # TODO Adicionar verificação do MissingName
        command_object = command_classe()

        command_name = command_object.command_name.lower()

        if command_name in self.commands_map:
            raise DuplicateFeatureNameError(f"Comando {command_name} já registrado")

        self.commands_map[command_name] = command_object

        command_aliases = command_object.command_aliases
        command_aliases = [alias.lower() for alias in command_aliases]

        for alias in command_aliases:
            if alias in self.commands_map:
                raise DuplicateFeatureNameError(f"Alias {alias} já registrado. Comando de origem: {command_name}")

            self.commands_map[alias] = command_object

    def register_listener(self, listener_class: Type[BaseListener]):
        listener_object = listener_class()
        raw_types = listener_object.listener_type
        listener_name = listener_object.listener_name

        if not listener_name:
            raise MissingFeatureNameError(f"Listener {listener_class.__name__} não possui um nome definido")

        if listener_name in self.registered_names:
            raise DuplicateFeatureNameError(f"Listener com o nome {listener_name} já registrado")

        self.registered_names.add(listener_name)

        types_to_register = raw_types if isinstance(raw_types, (list, tuple, set)) else [raw_types]

        for listener_type in types_to_register:
            if not isinstance(listener_type, ListenerEventType):
                raise WrongTypeFeatureError(f"Listener {listener_name} ({listener_class.__name__}) está com o tipo errado")

            if listener_object in self.listener_map[listener_type]:
                continue

            self.listener_map[listener_type].append(listener_object)
