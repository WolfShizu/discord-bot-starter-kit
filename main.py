import os
import asyncio
from dotenv import load_dotenv

from app.discord_client import DiscordClient

# <--- Telemetria e terminal --->
from rich.live import Live

from app.core.telemetry import Telemetry
from app.core.dashboard import TerminalDashboard

load_dotenv()
discord_token = str(os.getenv("DISCORD_TOKEN"))

dashboard = TerminalDashboard()

telemetry = Telemetry(dashboard)

bot_instance = DiscordClient(dashboard, telemetry)

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
