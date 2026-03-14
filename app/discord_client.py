import os
import sys
from typing import cast
import asyncio
from datetime import datetime

import discord
from discord import app_commands

import psutil

from app.message_handler import MessageHandler
from app.core.exceptions.exception_handler import ExceptionHandler

from app.core.telemetry import Telemetry, SystemStatistics
from app.core.dashboard import TerminalDashboard

class DiscordClient(discord.Client):
    def __init__(self, dashboard: TerminalDashboard, telemetry: Telemetry):
        # Configura os privilégios do bot e o que ele receberá
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True

        super().__init__(intents=intents)

        self.dashboard = dashboard
        self.telemetry = telemetry

        self.exception_handler = ExceptionHandler()
        self.message_handler = MessageHandler(self.exception_handler, telemetry)

        self.statistics = SystemStatistics(
            system_status= "Starting...",
            connected_as= "",
            bot_id= 0,
            cpu_usage= "0%",
            ram_usage= "0%",
            uptime= "00:00:00",
            guilds= 0,
            processed_messages= 0,
            messages_sent= 0,
            features_executed= 0,
            commands_executed= 0,
            listeners_executed= 0
        )

        self.start_time = datetime.now()

    # <---- Primeiro evento de conexão ---->
    async def on_ready(self) -> None:
        ...

    # <---- Configuração da Telemetria ---->
    async def setup_hook(self) -> None:
        self.loop.create_task(self.telemetry_task())

    async def telemetry_task(self) -> None:
        await self.wait_until_ready()

        while not self.is_closed():
            self.statistics.system_status = "Online"
            self.statistics.connected_as = cast(str, self.user)
            self.statistics.bot_id = self.user.id if self.user else 0
            self.statistics.guilds = len(self.guilds)

            self.statistics.uptime = self._get_uptime()

            self.statistics.cpu_usage = f"{psutil.cpu_percent()}%"

            process = psutil.Process(os.getpid()) # Pega o ID do processo atual do bot
            memory_info = process.memory_info()

            # rss (Resident Set Size) é a memória física real que o processo está usando
            ram_usage = memory_info.rss / (1024 ** 2)

            self.statistics.ram_usage = f"{ram_usage:.2f}MB"

            self.dashboard.update_statistics(self.statistics)

            await asyncio.sleep(1)

    def _get_uptime(self) -> str:
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # <---- Eventos de Mensagens ---->
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        self.statistics.processed_messages += 1
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
