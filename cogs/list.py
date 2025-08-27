import discord
from discord.ext import commands
import math

class PlaylistView(discord.ui.View):
    def __init__(self, ctx: commands.Context, queue: list, current_track: str, total_tracks: int, per_page: int = 8):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.queue = queue
        self.current_track = current_track
        self.total_tracks = total_tracks
        self.per_page = per_page
        self.current_page = 0
        self.max_page = math.ceil(len(self.queue) / per_page) if self.queue else 1
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page >= self.max_page - 1)

    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(color=0xFFCCFF)
        avatar_url = self.ctx.author.avatar.url if self.ctx.author.avatar else self.ctx.author.default_avatar.url
        embed.set_author(name="Danh sách phát", icon_url=avatar_url)
        description = f"<:music_box:1345662659109982299> Bài hát đang phát: {self.current_track} <:music_box:1345662659109982299>\n\n"
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_items = self.queue[start:end]
        if page_items:
            for i, track in enumerate(page_items, start=start+1):
                if isinstance(track, tuple):
                    title = track[1]
                else:
                    title = track.title
                description += f"{i}. {title}\n"
        else:
            description += "Danh sách phát trống."
        embed.description = description
        embed.set_footer(text=f"Tổng {self.total_tracks} bài hát")
        return embed

    @discord.ui.button(label="Trang trước", style=discord.ButtonStyle.secondary, custom_id="previous")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = self.generate_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Trang sau", style=discord.ButtonStyle.secondary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_page - 1:
            self.current_page += 1
            self.update_buttons()
            embed = self.generate_embed()
            await interaction.response.edit_message(embed=embed, view=self)

class ListCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="list")
    async def list_command(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description="Bot không ở trong kênh voice nào!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        vc = ctx.voice_client

        current_track_obj = getattr(vc, "current", None)
        if current_track_obj is None:
            current_track_text = "Không có bài nào đang phát"
        else:
            current_track_text = current_track_obj.title

        queue = getattr(vc, "custom_queue", [])
        total_tracks = (1 if current_track_obj is not None else 0) + len(queue)

        view = PlaylistView(ctx, queue, current_track_text, total_tracks, per_page=8)
        embed = view.generate_embed()
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(ListCommand(bot))
