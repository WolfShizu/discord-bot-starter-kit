import functools

import discord

from app.models.message_payload import UserMessagePayload, BotResponsePayload
from app.gatekeeper import Gatekeeper

class MessageHandler:
    def __init__(self, gatekeeper: Gatekeeper):
        self.gatekeeper = gatekeeper
    
    async def handle_message(self, message: discord.Message):
        raw_message = message.content

        # TODO Passar a mensagem pelo Gatekeeper
        
        user_message_payload = UserMessagePayload(
            message= message,
            send_message_function= functools.partial(self.send_message, channel= message.channel),
            raw_message= raw_message,
            is_private_message= message.guild is None
        )
    
    async def send_message(self, response_payload: BotResponsePayload, channel: discord.abc.Messageable):
        if response_payload.embed:
            await channel.send(embed= response_payload.embed)
        await channel.send(response_payload.content)