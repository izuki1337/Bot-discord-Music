import discord
import random
from discord.ext import commands, tasks
from datetime import datetime
import asyncio

class TrangThai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
        self.status_messages = ["yea I love music 🎶"]
        self.message_index = 0
        self.update_status.start()

    @tasks.loop(seconds=20)
    async def update_status(self):
        current_time = datetime.now()
        uptime = current_time - self.start_time 
        hours, remainder = divmod(uptime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        status_message = self.status_messages[self.message_index]
        activity = discord.Activity(type=discord.ActivityType.watching, name=status_message)
        await self.bot.change_presence(status=discord.Status.idle, activity=activity)

        self.message_index = (self.message_index + 1) % len(self.status_messages)

    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()


    @commands.Cog.listener()
    async def on_ready(self):
        print('_________________________')
        print('bot qua dz ')
        print('__________________________')

async def setup(bot):
    await bot.add_cog(TrangThai(bot))
