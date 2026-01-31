from typing import Any

class Dispatcher:
    def __init__(self):
        self.commands: dict[str, Any] = {}
    
    def register_command(self, command_name: str, command_aliases: list[str]):
        def wrapper(command_class):
            command_instance = command_class()

            command_instance.name = command_name.lower()
            command_instance.aliases = [command.lower() for command in command_aliases]

            # TODO Fazer uma verificação no self.commands. Verificar se o comando já foi registrado. Se sim, deve retornar um erro
            self.commands[command_instance.name] = command_instance

            for alias in command_instance.aliases:
                self.commands[alias] = command_instance

                return command_instance
            
        return wrapper