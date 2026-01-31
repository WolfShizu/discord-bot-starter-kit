import functools

import discord

from app.models.message_payload import UserMessagePayload, BotResponsePayload
from app.gatekeeper import Gatekeeper
from app.dispatcher import Dispatcher

class MessageHandler:
    def __init__(self):
        self.gatekeeper = Gatekeeper()
        self.Dispatcher = Dispatcher(self.send_message)
    
    async def handle_message(self, message: discord.Message):
        raw_message = message.content
        
        user_message_payload = UserMessagePayload(
            message= message,
            send_message_function= functools.partial(self.send_message, channel= message.channel),
            raw_message= raw_message,
            is_private_message= message.guild is None
        )

        self.gatekeeper.verify_message(user_message_payload)

        self.Dispatcher.dispatch(user_message_payload)
    
    async def send_message(self, response_payload: BotResponsePayload, channel: discord.abc.Messageable):
        """
        Função para envio de mensagens utilizada pelos comandos e listeners
        """
        # TODO Implementar o send_to do payload
        if response_payload.embed:
            await channel.send(embed= response_payload.embed)
        await channel.send(response_payload.content)