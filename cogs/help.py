import discord
from discord.ext import commands
import datetime

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')  # Remove default help command
    
    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx, command=None):
        """Shows help for bot commands"""
        if command is None:
            # Create main help embed
            embed = discord.Embed(
                title="Music Bot Commands",
                description="Use `help [command]` for more information about a specific command.",
                color=discord.Color.darker_gray(),
                timestamp=datetime.datetime.utcnow()
            )
            
            # Music commands
            music_commands = "`nplay`, `npause`, `nresume`, `nskip`, `nstop`, `nqueue`, `nnow_playing`"
            embed.add_field(name="🎵 Music", value=music_commands, inline=False)
            
            # Playlist commands
            playlist_commands = "`nsave_playlist`, `nload_playlist`, `nlist_playlists`"
            embed.add_field(name="📋 Playlists", value=playlist_commands, inline=False)
            
            # Utility commands
            utility_commands = "`nhelp`, `nping`"
            embed.add_field(name="🔧 Utility", value=utility_commands, inline=False)
            
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            
            await ctx.send(embed=embed)
        else:
            # Get the command
            cmd = self.bot.get_command(command)
            if cmd is None:
                await ctx.send(f"Command `{command}` not found.")
                return
            
            # Create command help embed
            embed = discord.Embed(
                title=f"Command: {cmd.name}",
                description=cmd.help or "No description provided.",
                color=discord.Color.darker_gray(),
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add aliases if any
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join([f"`{alias}`" for alias in cmd.aliases]), inline=False)
            
            # Add usage
            embed.add_field(name="Usage", value=f"`{cmd.name} {cmd.signature}`", inline=False)
            
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))