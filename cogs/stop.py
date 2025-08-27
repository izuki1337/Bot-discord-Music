import discord
from discord.ext import commands
import wavelink

class Stop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="stop", aliases=["s"])
    async def stop_command(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description="Bot không ở trong kênh voice nào!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        
        vc: wavelink.Player = ctx.voice_client

        if not hasattr(vc, "ctx") or (vc.ctx.author.id != ctx.author.id and not ctx.author.guild_permissions.manage_guild):
            embed = discord.Embed(
                description="Chỉ người đã dùng lệnh `play` hoặc người có quyền `manage server` mới có thể sử dụng lệnh `stop`!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        
        if hasattr(vc, "custom_queue"):
            vc.custom_queue.clear()
        
        music_script = self.bot.get_cog("MusicScript")
        if music_script:
            music_script.mark_stopped(ctx.guild)
        
        await vc.stop()
        await vc.disconnect()
        
        embed = discord.Embed(
            description="**Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi <:heart:1335171872404537384>**",
            color=0xFFCCFF
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Stop(bot))
