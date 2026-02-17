# TODO Configurar o event type do listener
# TODO Configurar o listener type do Listener, para definir se ele deve vir antes ou depois de comandos, ou se ele não deve ser chamado caso um comando seja executado

from typing import Any, Type

from app.commands.base import BaseCommand, BaseListener
from app.models.message_payload import UserMessagePayload

class Dispatcher:
    """
    Classe responsável por enviar os payloads para as funções, além de registrá-los
    """
    def __init__(self):
        self.commands_map: dict[str, Any] = {}
        self.listeners_list: list[Any] = [] # TODO Alterar para dicionário para acomodar os events types e listener types

    async def dispatch(self, message_payload: UserMessagePayload):
        # Passa a mensagem para os listeners
        for listener in self.listeners_list:
            await listener.handle_event(message_payload)

        # Executa o comando, se houver
        if message_payload.is_command and isinstance(message_payload.command_name, str):
            command = self.commands_map.get(message_payload.command_name.lower())

            if command:
                await command.execute_command(message_payload)

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

        if listener_object in self.listeners_list:
            raise ValueError(f"Listener {listener_object.listener_name} já registrado!")

        self.listeners_list.append(listener_object)
