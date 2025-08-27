import discord
import random
from discord.ext import commands
import wavelink

class Shuffle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description="Bot không ở trong kênh voice nào!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        
        vc: wavelink.Player = ctx.voice_client

        if not hasattr(vc, "ctx") or (vc.ctx.author.id != ctx.author.id and not ctx.author.guild_permissions.manage_guild):
            embed = discord.Embed(
                description="Chỉ người đã dùng lệnh `play` hoặc người có quyền `manage server` mới có thể sử dụng lệnh `shuffle`!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        
        if not hasattr(vc, "custom_queue") or not vc.custom_queue:
            embed = discord.Embed(
                description="Danh sách phát trống!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        
        random.shuffle(vc.custom_queue)
        embed = discord.Embed(
            description="**Danh sách phát đã được xáo trộn** <:music_box:1345662659109982299>",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Shuffle(bot))
