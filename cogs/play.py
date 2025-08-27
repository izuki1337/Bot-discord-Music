import discord
import asyncio
import re
import wavelink
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="78e3372c57534943bd4b956b5f89f98e",
            client_secret="2300911ebb414550a1935f8b58f42ea3"
        ))
        self.search_semaphore = asyncio.Semaphore(5)
        asyncio.create_task(self.setup_nodes())
        asyncio.create_task(self.auto_play_loop())

    async def setup_nodes(self):
        await self.bot.wait_until_ready()
        nodes = [
            wavelink.Node(
                uri="https://lava-v4.ajieblogs.eu.org:443",
                password="https://dsc.gg/ajidevserver",
                identifier="Main Node"
            )
        ]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot)

    async def safe_search(self, query: str, retries: int = 3):
        for attempt in range(1, retries + 1):
            try:
                async with self.search_semaphore:
                    results = await wavelink.Playable.search(query)
                if results:
                    return results
            except Exception as e:
                if "429" in str(e):
                    wait_time = attempt * 2
                    print(f"429 error cho query '{query}' - lần thử {attempt}, chờ {wait_time} giây.")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
        return None

    async def fetch_spotify_playlist_tracks(self, url: str):
        pattern = r"playlist/([a-zA-Z0-9]+)"
        match = re.search(pattern, url)
        if not match:
            return []
        playlist_id = match.group(1)
        playlist = await asyncio.to_thread(self.sp.playlist, playlist_id)
        track_queries = []
        for item in playlist['tracks']['items']:
            track = item['track']
            artists = ", ".join([artist['name'] for artist in track['artists']])
            query = f"{track['name']} {artists}"
            track_queries.append(query)
        return track_queries

    async def load_track(self, item):
        if isinstance(item, tuple):
            loader, query = item
            results = await loader(query)
            if results:
                return results[0]
            else:
                return None
        else:
            return item

    @commands.command(name="play", aliases=["p"])
    async def play_command(self, ctx: commands.Context, url: str):
        if ("list=" in url) or ("soundcloud.com" in url and "/sets/" in url):
            try:
                result = await wavelink.Playable.search(url)
            except Exception as e:
                embed = discord.Embed(
                    description=f"Lỗi khi tải playlist: {e}",
                    color=0xFF0000
                )
                return await ctx.send(embed=embed)
            
            if isinstance(result, list):
                tracks = result
            elif hasattr(result, "tracks"):
                tracks = result.tracks
            else:
                tracks = [result]

        elif "open.spotify.com/playlist" in url:
            try:
                track_queries = await self.fetch_spotify_playlist_tracks(url)
                tracks = [(self.safe_search, query) for query in track_queries]
            except Exception as e:
                embed = discord.Embed(
                    description=f"Lỗi khi tải playlist Spotify: {e}",
                    color=0xFF0000
                )
                return await ctx.send(embed=embed)
        
        else:
            try:
                search_results = await self.safe_search(url)
            except Exception as e:
                embed = discord.Embed(
                    description=f"Lỗi khi tải bài hát: {e}",
                    color=0xFF0000
                )
                return await ctx.send(embed=embed)
            
            if not search_results:
                embed = discord.Embed(
                    description="Không tìm thấy bài hát nào từ link bạn cung cấp!",
                    color=0xFF0000
                )
                return await ctx.send(embed=embed)
            tracks = [search_results[0]]
        
        if not tracks:
            embed = discord.Embed(
                description="Không thể tìm thấy bài hát từ playlist!",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)
        
        if not ctx.voice_client:
            if not ctx.author.voice:
                embed = discord.Embed(
                    description="Bạn chưa ở kênh voice nào!",
                    color=0xFF0000
                )
                return await ctx.send(embed=embed)
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True, self_mute=False)
            vc.notification_channel = ctx.channel
            vc.custom_queue = []
            music_script = self.bot.get_cog("MusicScript")
            if music_script:
                music_script.set_notification_channel(ctx.guild, ctx.channel)
        else:
            vc: wavelink.Player = ctx.voice_client
            vc.notification_channel = ctx.channel
            if not hasattr(vc, "custom_queue"):
                vc.custom_queue = []
            music_script = self.bot.get_cog("MusicScript")
            if music_script:
                music_script.set_notification_channel(ctx.guild, ctx.channel)
        
        if vc.playing:
            vc.custom_queue.extend(tracks)
            if len(tracks) > 1:
                embed = discord.Embed(
                    description=f"Đã thêm playlist gồm {len(tracks)} bài vào danh sách phát! <:music_box:1345662659109982299>",
                    color=0x00FF00
                )
            else:
                embed = discord.Embed(
                    description=f"Đã thêm **{tracks[0] if not isinstance(tracks[0], tuple) else 'bài mới' }** vào danh sách phát! <:music_box:1345662659109982299>",
                    color=0x00FF00
                )
            return await ctx.send(embed=embed)
        else:
            first_item = tracks.pop(0)
            first_track = await self.load_track(first_item)
            if not first_track:
                embed = discord.Embed(
                    description="Không thể tải bài hát đầu tiên từ playlist!",
                    color=0xFF0000
                )
                return await ctx.send(embed=embed)
            vc.ctx = ctx
            await vc.play(first_track)
            embed = discord.Embed(
                description=f"**Bắt đầu chơi** {first_track.title} <:music_box:1345662659109982299>",
                color=0x00FF00
            )
            await ctx.send(embed=embed)
            if tracks:
                vc.custom_queue.extend(tracks)
                embed = discord.Embed(
                    description=f"Đã thêm **{len(tracks)}** vào danh sách phát! <:music_box:1345662659109982299>",
                    color=0x00FF00
                )
                await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload):
        player = payload.player
        if hasattr(player, "custom_queue") and player.custom_queue:
            next_item = player.custom_queue.pop(0)
            next_track = await self.load_track(next_item)
            if next_track:
                await player.play(next_track)
                notification_channel = getattr(player, 'notification_channel', None)
                if notification_channel:
                    embed = discord.Embed(
                        description=f"**Tiếp tục chơi** {next_track.title} <:music_box:1345662659109982299>",
                        color=0x00FF00
                    )
                    await notification_channel.send(embed=embed)
            else:
                print("Không tải được track tiếp theo.")

    async def auto_play_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for vc in self.bot.voice_clients:
                if isinstance(vc, wavelink.Player) and not vc.playing and hasattr(vc, "custom_queue") and vc.custom_queue:
                    try:
                        next_item = vc.custom_queue.pop(0)
                        next_track = await self.load_track(next_item)
                        if next_track:
                            await vc.play(next_track)
                            if hasattr(vc, 'notification_channel') and vc.notification_channel:
                                embed = discord.Embed(
                                    description=f"**Tiếp tục chơi** {next_track.title} <:music_box:1345662659109982299>",
                                    color=0x00FF00
                                )
                                await vc.notification_channel.send(embed=embed)
                        else:
                            print("Không tải được track tiếp theo trong auto_play_loop.")
                    except Exception as e:
                        print(f"Lỗi trong auto_play_loop: {e}")
            await asyncio.sleep(5)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
