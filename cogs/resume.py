import discord
from discord.ext import commands
import wavelink

class Resume(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="resume")
    async def resume_command(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description="Bot không ở trong kênh voice nào!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        vc: wavelink.Player = ctx.voice_client

        if not hasattr(vc, "ctx") or (vc.ctx.author.id != ctx.author.id and not ctx.author.guild_permissions.manage_guild):
            embed = discord.Embed(
                description="Chỉ người đã dùng lệnh `play` hoặc người có quyền `manage server` mới có thể sử dụng lệnh `resume`!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        try:
            await vc.pause(False)
        except Exception as e:
            embed = discord.Embed(
                description=f"Lỗi khi tiếp tục phát: {e}",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            description="**Bài hát được tiếp tục phát** <:music_box:1345662659109982299>",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Resume(bot))
