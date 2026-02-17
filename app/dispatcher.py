# TODO Configurar o event type do listener
# TODO Configurar o listener type do Listener, para definir se ele deve vir antes ou depois de comandos, ou se ele não deve ser chamado caso um comando seja executado

from typing import Any, Callable, Coroutine

from app.commands.base import BaseCommand, BaseListener
from app.models.message_payload import UserMessagePayload

class Dispatcher:
    """
    Classe responsável por enviar os payloads para as funções, além de registrá-los
    """
    def __init__(self, send_message_function: Callable[[Any, Any], Coroutine[Any, Any, None]]):
        self.send_message_function = send_message_function

        self.commands_map: dict[str, Any] = {}
        self.listeners_list: list[Any] = [] # TODO Alterar para dicionário para acomodar os events types e listener types

    async def dispatch(self, message_payload: UserMessagePayload):
        # Passa a mensagem para os listeners
        for listener in self.listeners_list:
            listener.handle_event(message_payload)

        # Executa o comando, se houver
        if message_payload.is_command and isinstance(message_payload.command_name, str):
            command = self.commands_map.get(message_payload.command_name.lower())

            if command:
                command.execute_command(message_payload)
