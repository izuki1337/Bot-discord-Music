import discord
from discord.ext import commands
import wavelink

class Skip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="skip")
    async def skip_command(self, ctx: commands.Context):
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
                description="Chỉ người đã dùng lệnh `play` hoặc người có quyền `manage server` mới có thể sử dụng lệnh `skip`!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        
        current_track = getattr(vc, "current", None)
        track_title = current_track.title if current_track and hasattr(current_track, "title") else "Bài hát hiện tại"
        
        await vc.stop()
        
        embed = discord.Embed(
            description=f"**{track_title}** đã được bỏ qua <:music_box:1345662659109982299>",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Skip(bot))
