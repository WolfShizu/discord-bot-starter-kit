import os
import asyncio
from dotenv import load_dotenv

from app.discord_client import DiscordClient

# <--- Telemetria e terminal --->
from rich.live import Live

from app.core.telemetry import Telemetry, TerminalDashboard


load_dotenv()
discord_token = str(os.getenv("DISCORD_TOKEN"))

telemetry = Telemetry()

bot_instance = DiscordClient(telemetry)

# roda o bot de forma assíncrona
async def main():
    async with bot_instance:
        await bot_instance.start(token= discord_token)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
