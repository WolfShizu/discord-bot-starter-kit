from typing import cast

import discord

from app.models.message_payload import UserMessagePayload

from app.core.exceptions.exception_handler import ExceptionHandler

class Gatekeeper:
    """
    Classe responsável por verificar as mensagens, definir as permissões do usuário no payload e fazer o parse do comando
    """
    def __init__(self, exception_handler: ExceptionHandler, default_prefix: str = "!"):
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
        """
        Verifica se a mensagem tem algum conteúdo, se é um comando e as permissões do usuário.
        Essas informações são guardadas dentro do payload.
        """
        if message_payload.is_private_message:
            return # TODO Fazer a verificação de comando. Ainda não faz o processo de mensagens via DM

        self._set_user_access(message_payload)

        # Caso a mensagem esteja vazia, automaticamente ela não é um comando
        if not message_payload.raw_message or message_payload.raw_message.strip() == "":
            message_payload.is_command = False
            return

        # Busca o prefixo usado pelo bot
        guild_id = message_payload.message.guild.id if message_payload.message.guild else None
        if guild_id:
            bot_prefix = self.guild_prefix_map.get(guild_id, self.default_prefix)
        else:
            bot_prefix = self.default_prefix

        # Define se a mensagem é um comando
        if message_payload.raw_message.startswith(bot_prefix):
            message_payload.is_command = True

            self._parse_command(message_payload, bot_prefix)


    def _set_user_access(self, message_payload: UserMessagePayload):
        """
        Verifica e armazena as informações de acesso do usuário.
        Verifica se ele é um admin e se está bloqueado ou proibido de usar o canal.
        """
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
            message_payload.is_authorized_role = False
            return message_payload

        if any(role_id in channel_access_map["allowed_roles"] for role_id in user_roles):
            message_payload.is_authorized_role = True
            return message_payload

    def _parse_command(self, message_payload: UserMessagePayload, bot_prefix: str):
        """
        Armazena o comando do bot (sem prefixo) e os argumentos
        """
        raw_message = str(message_payload.raw_message).strip()

        parts = raw_message.split()
        raw_command = parts[0]
        message_payload.command_name = raw_command.removeprefix(bot_prefix).lower()
        message_payload.arguments = parts[1:]
