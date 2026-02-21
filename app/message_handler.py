import functools
import os
import importlib
import inspect

import discord

from app.models.message_payload import UserMessagePayload, BotResponsePayload

from app.features.commands.base_command import BaseCommand
from app.features.listeners.base_listener import BaseListener

from app.gatekeeper import Gatekeeper
from app.dispatcher import Dispatcher

class MessageHandler:
    """
    Classe principal responsável por gerenciar as mensagens. Envia o payload do usuário
    para as outras funções, além de gerenciar o envio de mensagens do bot
    """
    def __init__(self):
        self.gatekeeper = Gatekeeper()
        self.dispatcher = Dispatcher()

        self._load_commands_and_listeners()

    async def handle_message(self, message: discord.Message):
        raw_message = message.content

        user_message_payload = UserMessagePayload(
            message= message,
            send_message_function= functools.partial(self.send_message, channel= message.channel),
            raw_message= raw_message,
            is_private_message= message.guild is None
        )

        self.gatekeeper.verify_message(user_message_payload)

        await self.dispatcher.dispatch(user_message_payload)

    async def send_message(self, response_payload: BotResponsePayload, channel: discord.abc.Messageable):
        """
        Função para envio de mensagens utilizada pelos comandos e listeners
        """
        # TODO Implementar o send_to do payload
        if response_payload.embed:
            await channel.send(embed= response_payload.embed)
        await channel.send(response_payload.content)

    def _load_commands_and_listeners(self):
        """
        Busca e registra todos os comandos e listeners em app/commands
        """
        # Caminho: app/commands/instances
        commands_path = os.path.join(os.path.dirname(__file__), "features")

        for root, _, files in os.walk(commands_path):
            for file in files:
                if file.endswith(".py") and file not in ["base.py", "__init__.py"]:
                    relative_path = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))
                    module_path = "app." + relative_path.replace(os.sep, ".").removesuffix(".py")

                    try:
                        module = importlib.import_module(module_path)

                        for _, object_class in inspect.getmembers(module):
                            if (
                                inspect.isclass(object_class) and
                                not inspect.isabstract(object_class)
                            ):
                                if issubclass(object_class, BaseCommand) and object_class is not BaseCommand:
                                    # TODO Adicionar aviso para comandos sem nome
                                    if getattr(object_class, "command_name", None):
                                        self.dispatcher.register_command(object_class)

                                if issubclass(object_class, BaseListener) and object_class is not BaseListener:
                                    self.dispatcher.register_listener(object_class)

                    except Exception as error:
                        print(f"Erro ao carregar módulo: {module_path}: {error}")
