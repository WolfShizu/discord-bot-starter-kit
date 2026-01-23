import os
import asyncio
from dotenv import load_dotenv

from app.discord_client import DiscordClient
from app.message_handler import MessageHandler

load_dotenv()
discord_token = str(os.getenv("DISCORD_TOKEN"))

message_handler = MessageHandler()
bot_instance = DiscordClient(message_handler)

# roda o bot de forma assíncrona
async def main():
    async with bot_instance:
        await bot_instance.start(token= discord_token)

asyncio.run(main())