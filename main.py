import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='n', intents=intents, help_command=None)

async def load_extensions():
    initial_extensions = [
    "cogs.play",
    "cogs.clear",
    "cogs.list",
    "cogs.music_script",
    "cogs.pause",
    "cogs.repeat",
    "cogs.resume",
    "cogs.stop",
    "cogs.skip",
    "cogs.shuffle",
    "cogs.combined",
    "cogs.help",
    "cogs.TrangThai",

    ]
    
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv('TOKEN')
        if token is None:
            raise ValueError("No TOKEN found in environment variables. Please check your .env file.")
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())


