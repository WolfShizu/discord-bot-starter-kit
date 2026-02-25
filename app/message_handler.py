import functools
import os
import importlib
import inspect
from typing import cast

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
        message_id = message.id

        user_message_payload = UserMessagePayload(
            message= message,
            send_message_function= functools.partial(self.send_message, channel= message.channel),
            author_id= message.author.id,
            guild_id= message.guild.id if message.guild else None,
            raw_message= raw_message,
            message_id = message_id,
            is_private_message= message.guild is None
        )

        self.gatekeeper.verify_message(user_message_payload)

        await self.dispatcher.dispatch_message(user_message_payload)

    async def send_message(self, response_payload: BotResponsePayload, channel: discord.abc.Messageable):
        """
        Função para envio de mensagens utilizada pelos comandos e listeners
        """
        send_kwargs = {}
        if response_payload.reply_to:
            channel_id = cast(int, getattr(channel, "id", None))
            if channel_id:
                reference = discord.MessageReference(
                    message_id= response_payload.reply_to,
                    channel_id= channel_id
                )
                send_kwargs["reference"] = reference
            else:
                # TODO Tratar corretamente o erro
                print("Aviso: Não foi possível obter o ID do canal para criar a referência da mensagem. Enviando sem referência.")

        if response_payload.embed:
            send_kwargs["embed"] = response_payload.embed

        if response_payload.content:
            send_kwargs["content"] = response_payload.content

        try:
            await channel.send(**send_kwargs)
        except Exception as error:
            # TODO Tratar corretamente o erro
            print(f"Falha no envio de mensagem: {error}")
        return


    def _load_commands_and_listeners(self):
        """
        Busca e registra todos os comandos e listeners em app/commands
        """
        # Caminho: app/features
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
