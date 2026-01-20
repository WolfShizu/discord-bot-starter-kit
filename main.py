import os
import asyncio
from dotenv import load_dotenv

from discord_client import DiscordClient

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")

bot = DiscordClient()

# roda o bot de forma assíncrona
async def main():
    async with bot:
        await bot.start(discord_token)

asyncio.run(main())