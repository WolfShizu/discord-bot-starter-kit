import os
import asyncio
from dotenv import load_dotenv

from app.discord_client import DiscordClient

# <--- Telemetria e terminal --->
from rich.live import Live

from app.core.telemetry import Telemetry
from app.core.dashboard import TerminalDashboard
from app.core.telemetry import SystemStatistics

load_dotenv()
discord_token = str(os.getenv("DISCORD_TOKEN"))

dashboard = TerminalDashboard()

statistics = SystemStatistics(
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

telemetry = Telemetry(dashboard, statistics)

bot_instance = DiscordClient(dashboard, telemetry, statistics)

# roda o bot de forma assíncrona
async def main():
    with Live(dashboard.layout, refresh_per_second=4, screen=True):
        dashboard.add_log("Iniciando sistema", style="yellow")

        async with bot_instance:
            await bot_instance.start(token= discord_token)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
