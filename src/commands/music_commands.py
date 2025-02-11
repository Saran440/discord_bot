import discord
import yt_dlp
import asyncio
from discord import app_commands
from discord.ext import commands

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    async def join_voice_channel(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return None

        voice_channel = interaction.user.voice.channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        return voice_client

    def search_youtube(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch1',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return info['url'], info['title']

    async def play_next(self, interaction):
        if interaction.guild.id in self.queues and self.queues[interaction.guild.id]:
            url, title = self.queues[interaction.guild.id].pop(0)
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if voice_client and voice_client.is_connected():
                source = await discord.FFmpegOpusAudio.from_probe(url, method='fallback')
                voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop))
                await interaction.channel.send(f'🎶 Now playing: **{title}**')
        else:
            await interaction.channel.send("🎵 Queue is empty! Leaving voice channel.")
            await self.disconnect(interaction)

    @app_commands.command(name="song", description="Play a song from YouTube")
    async def play_song(self, interaction: discord.Interaction, search: str):
        """Search and play a song from YouTube"""
        await interaction.response.defer()

        voice_client = await self.join_voice_channel(interaction)
        if not voice_client:
            return

        url, title = self.search_youtube(search)
        if not url:
            await interaction.followup.send("❌ Could not find the song.")
            return

        if interaction.guild_id not in self.queues:
            self.queues[interaction.guild_id] = []

        self.queues[interaction.guild_id].append((url, title))

        if not voice_client.is_playing():
            await self.play_next(interaction)
        else:
            await interaction.followup.send(f'🎵 Added to queue: **{title}**')

    @app_commands.command(name="song_end", description="Stop the current song and clear the queue")
    async def stop_song(self, interaction: discord.Interaction):
        """Stop the current song and clear the queue"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            self.queues[interaction.guild_id] = []
            await interaction.response.send_message("⏹️ Stopped playback and cleared queue.")
        else:
            await interaction.response.send_message("⚠️ No song is currently playing.")

    async def disconnect(self, interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client:
            await voice_client.disconnect()
            await interaction.channel.send("📴 Disconnected from voice channel.")

async def setup(bot):
    await bot.add_cog(MusicBot(bot))
