import sys

import discord
from discord import app_commands

from app.message_handler import MessageHandler
from app.core.exceptions.exception_handler import ExceptionHandler

class DiscordClient(discord.Client):
    def __init__(self):
        self.message_handler = MessageHandler()
        self.exception_handler = ExceptionHandler()

        # Configura os privilégios do bot e o que ele receberá
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True

        super().__init__(intents=intents)

    # <---- Primeiro evento de conexão ---->
    async def on_ready(self) -> None:
        if isinstance(self.user, discord.ClientUser):
            bot_name = self.user.name
            bot_id = self.user.id
            total_guilds = len(self.guilds)

            print("=" * 30)
            print("SISTEMA ONLINE")
            print(f"Bot: {bot_name}")
            print(f"Bot ID: {bot_id}")
            print(f"Total de servidores: {total_guilds}")
            print("=" * 30)
        else:
            print("Falha ao obter informações do bot")

    # <---- Eventos de Mensagens ---->
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await self.message_handler.handle_message(message)


    async def on_message_edit(self, message):
        ...

    async def on_message_delete(self, message):
        ...

    async def on_raw_message_delete(self, message):
        """Para mensagens antigas que não estão no cache do bot"""
        ...

    # <---- Eventos de Conexão ---->
    async def on_connect(self):
        """Chamado quando o bot se conecta, seja na primeira conexão ou após uma queda"""
        ...

    async def on_disconnect(self):
        """Chamado quando o bot se desconecta"""
        ...

    async def on_resumed(self):
        """Quando o bot se desconecta, mas retorna a conexão rapidamente, sem perder o cache"""
        ...

    # <---- Eventos de Membros e Servidores ---->
    async def on_member_join(self, member):
        ...

    async def on_member_remove(self, member):
        """Quando um usuário saiu ou foi expulso"""
        ...

    async def on_member_update(self, before, after):
        """Mudança de cargo, apelido ou status"""
        ...

    async def on_guild_join(self, guild):
        """O bot foi adicionado em um servidor"""
        ...

    # <---- Eventos de Reação e Interação ---->
    async def on_reaction_add(self, reaction, user):
        ...

    async def on_interaction(self, interaction):
        """Alguém usou slash command ou um botão"""
        ...

    # <---- Tratamento de erro ---->
    async def on_error(self, event_method: str,*args, **kwargs):
        """Exceções da maioria dos eventos."""
        _, error_value, error_traceback = sys.exc_info()

        if error_value:
            await self.exception_handler.handle_exception(
                discord_event=event_method,
                event_arguments=args,
                exception=error_value,
                traceback=error_traceback
            )

    async def on_app_command_error(self, interaction: discord.Interaction, exception: app_commands.AppCommandError):
        """Exceções específicas de comandos slash"""
        await self.exception_handler.handle_exception(
            discord_event= "slash_command",
            event_arguments= tuple([interaction]),
            exception= exception,
            traceback= exception.__traceback__
        )
