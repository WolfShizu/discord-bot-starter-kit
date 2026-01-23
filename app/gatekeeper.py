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