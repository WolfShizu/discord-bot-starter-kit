from typing import cast

import discord

from app.models.message_payload import UserMessagePayload

class Gatekeeper:
    def __init__(self, default_prefix: str = "!"):
        self.default_prefix = default_prefix

        # TODO Buscar informação do banco de dados
        self.guild_prefix_map = {
            0000: "!"
        }

        # TODO Buscar informação do banco de dados
        self.channels_access_map = {
            0000: {                     # ID do chat
                "admin_roles": {
                    4001,
                    4002
                },
                "allowed_roles": {
                    1000,
                    1001,
                    1002
                },
                "denied_roles": {
                    1003,
                    1004
                },
                "allowed_users": {
                    2000,
                    2001
                },
                "denied_users": {
                    3001,
                    3002
                }
            }
        }

    def verify_message(self, message_payload: UserMessagePayload):
        # DONE TODO Verificar se o usuário pode usar o bot no canal
        # DONE TODO Verifica se a mensagem é um comando
        # TODO Se for um comando, definir no payload que é comando, e guardar as informações do comando (comando e argumentos)

        if message_payload.is_private_message:
            return # TODO Fazer a verificação de comando. Ainda não faz o processo de mensagens via DM
        
        self._set_user_access(message_payload)

        # Caso a mensagem esteja vazia, automaticamente ela não é um comando
        if not message_payload.raw_message or message_payload.raw_message.strip() == "":
            message_payload.is_command = False
            return

        # Define se a mensagem é um comando com base no prefixo do servidor
        guild_id = message_payload.message.guild.id if message_payload.message.guild else None
        if guild_id:
            prefix = self.guild_prefix_map.get(guild_id, self.default_prefix)
        else:
            prefix = self.default_prefix         
        
        if message_payload.raw_message.endswith(prefix):
            message_payload.is_command = True

    
    def _set_user_access(self, message_payload: UserMessagePayload):
        author = cast(discord.Member, message_payload.message.author)
        channel_id = message_payload.message.channel.id
        user_id = author.id
        user_roles = [role.id for role in author.roles]

        channel_access_map = self.channels_access_map.get(channel_id, None)

        if not channel_access_map:
            # TODO Significa que o bot não foi configurado no servidor. Ele deve passar por esse processo primeiro. Tratar isso corretamente.
            return message_payload

        if user_id in channel_access_map["admin_roles"]:
            message_payload.is_admin_role = True
            return message_payload
        
        if user_id in channel_access_map["denied_users"]:
            message_payload.is_authorized_user = False
            return message_payload
        
        if user_id in channel_access_map["allowed_users"]:
            message_payload.is_authorized_user = True
            return message_payload
        
        if any(role_id in channel_access_map["denied_roles"] for role_id in user_roles):
            message_payload.is_ahthorized_role = False
            return message_payload
        
        if any(role_id in channel_access_map["allowed_roles"] for role_id in user_roles):
            message_payload.is_ahthorized_role = True
            return message_payload