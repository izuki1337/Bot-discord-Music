import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import logging
import os

load_dotenv()
# Get the token from the environment variable

# Configure logging
logging.basicConfig(level=logging.INFO, filename='moderation.log',
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Combined(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked for {reason}')
        logging.info(f'{ctx.author} kicked {member} for {reason}')

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned for {reason}')
        logging.info(f'{ctx.author} banned {member} for {reason}')

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned')
                logging.info(f'{ctx.author} unbanned {user}')
                return

    @commands.command(name='giverole')
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx, member: discord.Member, role: discord.Role):
        if ctx.author.top_role <= role:
            await ctx.send("You cannot assign a role higher or equal to your own role.")
            return

        await member.add_roles(role)
        await ctx.send(f'Assigned {role.mention} to {member.mention}')
        logging.info(f'{ctx.author} assigned {role} to {member}')

    @commands.command(name='clear', help='Xóa một số lượng tin nhắn trong kênh hiện tại.')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("Số lượng phải lớn hơn 0.")
            return
        
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Đã xóa {len(deleted)} tin nhắn.", delete_after=5)


async def setup(bot):
    await bot.add_cog(Combined(bot))
