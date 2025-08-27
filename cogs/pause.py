import discord
from discord.ext import commands
import wavelink

def format_time(ms: int) -> str:
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

class Pause(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="pause")
    async def pause_command(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description="Bot không ở trong kênh voice nào!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        vc: wavelink.Player = ctx.voice_client

        if not vc.playing:
            embed = discord.Embed(
                description="Không có bài hát nào đang phát!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        if not hasattr(vc, "ctx") or (vc.ctx.author.id != ctx.author.id and not ctx.author.guild_permissions.manage_guild):
            embed = discord.Embed(
                description="Chỉ người đã dùng lệnh `play` hoặc người có quyền `manage server` mới có thể sử dụng lệnh `pause`!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        await vc.pause(True)

        current_position = vc.position
        formatted_current = format_time(current_position)

        embed = discord.Embed(
            description=f"Bài hát đã tạm dừng lúc **{formatted_current}** <:music_box:1345662659109982299>",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Pause(bot))
