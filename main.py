import os
import asyncio
from dotenv import load_dotenv

from app.discord_client import DiscordClient

load_dotenv()
discord_token = str(os.getenv("DISCORD_TOKEN"))

bot_instance = DiscordClient()

# roda o bot de forma assíncrona
async def main():
    async with bot_instance:
        await bot_instance.start(token= discord_token)

asyncio.run(main())