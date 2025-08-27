import discord
import asyncio
from discord.ext import commands

class MusicScript(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.disconnect_tasks = {}
        self.initiated_disconnect = {}
        self.last_play_channel = {}
        self.stopped_by_command = {}

    def get_notification_channel(self, guild: discord.Guild) -> discord.TextChannel:
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            return guild.system_channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
        return None

    def set_notification_channel(self, guild: discord.Guild, channel: discord.TextChannel):
        self.last_play_channel[guild.id] = channel

    def mark_stopped(self, guild: discord.Guild):
        """Đánh dấu rằng lệnh stop đã được sử dụng cho guild này."""
        self.stopped_by_command[guild.id] = True

    async def schedule_disconnect(self, guild: discord.Guild, voice_client: discord.VoiceClient):
        await asyncio.sleep(30)
        if not voice_client or not voice_client.channel:
            return
        if len(voice_client.channel.members) == 1:
            self.initiated_disconnect[guild.id] = True
            notification_channel = self.last_play_channel.get(guild.id)
            if notification_channel is None:
                notification_channel = getattr(voice_client, 'notification_channel', None)
            if notification_channel:
                embed = discord.Embed(
                    description="Không còn ai trong voice nên tôi đã rời voice",
                    color=0xFF0000
                )
                await notification_channel.send(embed=embed)
            await voice_client.disconnect()
        self.disconnect_tasks.pop(guild.id, None)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild
        voice_client = guild.voice_client

        if member.id == self.bot.user.id:
            if before.channel is not None and after.channel is None:
                if not self.initiated_disconnect.get(guild.id, False) and not self.stopped_by_command.get(guild.id, False):
                    notification_channel = self.last_play_channel.get(guild.id)
                    if notification_channel is None and voice_client:
                        notification_channel = getattr(voice_client, 'notification_channel', None)
                    if notification_channel:
                        embed = discord.Embed(
                            description="Tôi đã bị kick ra khỏi voice",
                            color=0xFF0000
                        )
                        await notification_channel.send(embed=embed)
            self.disconnect_tasks.pop(guild.id, None)
            self.initiated_disconnect.pop(guild.id, None)
            self.stopped_by_command.pop(guild.id, None)
            return

        if voice_client and voice_client.channel:
            if len(voice_client.channel.members) == 1:
                if guild.id not in self.disconnect_tasks:
                    self.disconnect_tasks[guild.id] = asyncio.create_task(
                        self.schedule_disconnect(guild, voice_client)
                    )
            else:
                task = self.disconnect_tasks.pop(guild.id, None)
                if task:
                    task.cancel()

async def setup(bot: commands.Bot):
    await bot.add_cog(MusicScript(bot))
