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

    def dispatch(self, message_payload: UserMessagePayload):
        # Passa a mensagem para os listeners
        for listener in self.listeners_list:
            listener.handle_event(message_payload)

        # Executa o comando, se houver
        if message_payload.is_command and isinstance(message_payload.command_name, str):
            command = self.commands_map.get(message_payload.command_name.lower())

            if command:
                command.execute_command(message_payload)


    # <---- Decorador para registrar comandos ---->
    def register_command(self, command_name: str, command_aliases: list[str]):
        def wrapper(command_class: type[BaseCommand]):
            command_instance = command_class(self.send_message_function)

            command_instance.name = command_name.lower()
            command_instance.aliases = [command.lower() for command in command_aliases]
            
            if self._verifiy_command_exists(command_instance.name):
                raise ValueError(f"Comando '{command_instance.name}' já registrado.") # TODO Alterar para exceção personalizada

            self.commands_map[command_instance.name] = command_instance

            for alias in command_instance.aliases:
                if self._verifiy_command_exists(alias):
                    raise ValueError(f"Alias '{alias}' já registrado.") # TODO Alterar para exceção personalizada
                self.commands_map[alias] = command_instance

            return command_class
            
        return wrapper
    
    def _verifiy_command_exists(self, command_name: str, ) -> bool:

        command = self.commands_map.get(command_name.lower())

        if command:
            return True
        
        return False
    
    # <---- Decorador para registrar listeners ---->
    def register_listener(self):
        def wrapper(command_class: type[BaseListener]):
            command_instance = command_class(self.send_message_function)

            if self._verify_listener_exists(command_class):
                raise ValueError(f"Listener '{command_class.__name__}' já registrado.") # TODO Alterar para exceção personalizada

            self.listeners_list.append(command_instance)

            return command_class
        return wrapper

    def _verify_listener_exists(self, listener_class: type[BaseListener]) -> bool:
        for listener in self.listeners_list:
            if isinstance(listener, listener_class):
                return True

        return False
