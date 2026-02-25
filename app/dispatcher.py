# TODO Configurar o event type do listener
# TODO Configurar o listener type do Listener, para definir se ele deve vir antes ou depois de comandos, ou se ele não deve ser chamado caso um comando seja executado

from typing import Any, Type
import time

from app.features.commands.base_command import BaseCommand
from app.features.listeners.base_listener import BaseListener

from app.features.listeners.enums import ListenerEventType

from app.models.message_payload import UserMessagePayload

from app.core.telemetry import Telemetry, TelemetryFeaturePayload
from app.core.types import FeatureType

class Dispatcher:
    """
    Classe responsável por enviar os payloads para as funções, além de registrá-los
    """
    def __init__(self):
        self.commands_map: dict[str, Any] = {}
        self.listener_map = {event_type: [] for event_type in ListenerEventType}
        self.registered_names = set()

        self.telemetry = Telemetry()

    async def dispatch_message(self, message_payload: UserMessagePayload):
        # Passa a mensagem para os listeners
        for listener in self.listener_map[ListenerEventType.MESSAGE]:
            await self._execute_listener(
                listener= listener,
                payload= message_payload
            )

        # Executa o comando, se houver
        if message_payload.is_command and isinstance(message_payload.command_name, str):
            command = self.commands_map.get(message_payload.command_name.lower())

            if command:
                await self._execute_command(
                    command= command,
                    payload= message_payload
                )

    async def _execute_command(self, command: BaseCommand, payload: UserMessagePayload):
        start_time = time.perf_counter()
        sucess = False
        error_type = None

        try:
            await command.execute_command(payload)
            sucess = True

        except Exception as error:
            error_type = type(error).__name__
            raise error

        finally:
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

            await self.telemetry.record(telemetry_data)

    async def _execute_listener(self, listener: BaseListener, payload: UserMessagePayload):
        start_time = time.perf_counter()
        sucess = False
        error_type = None

        try:
            await listener.handle_event(payload)
            sucess = True

        except Exception as error:
            error_type = type(error).__name__
            raise error

        finally:
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

            await self.telemetry.record(telemetry_data)

    def register_command(self, command_classe: Type[BaseCommand]):
        command_object = command_classe()

        command_name = command_object.command_name.lower()

        if command_name in self.commands_map:
            raise ValueError(f"Comando {command_name} já registrado!")

        self.commands_map[command_name] = command_object

        command_aliases = command_object.command_aliases
        command_aliases = [alias.lower() for alias in command_aliases]

        for alias in command_aliases:
            if alias in self.commands_map:
                raise ValueError(f"Alias {alias} já registrado!")

            self.commands_map[alias] = command_object

    def register_listener(self, listener_class: Type[BaseListener]):
        listener_object = listener_class()
        raw_types = listener_object.listener_type
        listener_name = listener_object.listener_name

        if not listener_name:
            raise ValueError(f"Listener {listener_class.__name__} não possui um nome definido!")

        if listener_name in self.registered_names:
            raise ValueError(f"Listener com o nome {listener_name} já registrado!")

        self.registered_names.add(listener_name)

        types_to_register = raw_types if isinstance(raw_types, (list, tuple, set)) else [raw_types]

        for listener_type in types_to_register:
            if not isinstance(listener_type, ListenerEventType):
                raise ValueError(f"Listener {listener_name} ({listener_class.__name__}) está com o tipo errado!")

            if listener_object in self.listener_map[listener_type]:
                continue

            self.listener_map[listener_type].append(listener_object)
