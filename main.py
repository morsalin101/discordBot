import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp

# Load environment variables
load_dotenv()

# Get Discord and Spotify credentials from .env
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

# Set up Spotify client
spotify_auth_manager = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI
)
spotify = spotipy.Spotify(auth_manager=spotify_auth_manager)

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Helper function to get YouTube audio stream URL for a song
def get_youtube_audio_url(song_name):
    """
    Fetch the direct audio stream URL for a given song name using yt-dlp.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,  # Suppress yt-dlp output
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            if "entries" in results and results["entries"]:
                return results["entries"][0]["url"]  # Direct audio stream URL
        except Exception as e:
            print(f"Error fetching YouTube URL: {e}")
            return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def join(ctx):
    """
    Command for the bot to join a voice channel.
    """
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send(f"Joined {channel.name}")
        else:
            await ctx.send("I'm already in a voice channel!")
    else:
        await ctx.send("You need to join a voice channel first!")

@bot.command()
async def leave(ctx):
    """
    Command for the bot to leave the voice channel.
    """
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command()
async def play(ctx, *, query: str):
    """
    Command to play a song.
    """
    if not ctx.voice_client:
        await ctx.send("I'm not in a voice channel! Use `!join` to make me join first.")
        return

    await ctx.send(f"Searching for '{query}'...")

    # Get the YouTube audio URL for the song
    youtube_audio_url = get_youtube_audio_url(query)
    if not youtube_audio_url:
        await ctx.send("Couldn't find a song matching that query.")
        return

    try:
        # Play the audio using FFmpeg
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        source = FFmpegPCMAudio(youtube_audio_url, executable="C:\\ffmpeg\\bin\\ffmpeg.exe")
        ctx.voice_client.play(source, after=lambda e: print(f"Playback finished: {e}"))
        await ctx.send(f"Now playing: {query}")
    except Exception as e:
        await ctx.send(f"An error occurred while trying to play the song: {e}")
        print(f"Error: {e}")

@bot.command()
async def stop(ctx):
    """
    Command to stop playback.
    """
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Playback stopped.")
    else:
        await ctx.send("No audio is playing!")

@bot.command()
async def track(ctx, *, query: str):
    """
    Searches Spotify for a track and provides details.
    """
    try:
        # Search for the track on Spotify
        results = spotify.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_name = track['name']
            track_artist = ", ".join(artist['name'] for artist in track['artists'])
            track_url = track['external_urls']['spotify']

            response = (
                f"**Track Name:** {track_name}\n"
                f"**Artist(s):** {track_artist}\n"
                f"**Spotify URL:** {track_url}"
            )
            await ctx.send(response)
        else:
            await ctx.send("Sorry, I couldn't find any tracks matching that query.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def pause(ctx):
    """
    Command to pause playback.
    """
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Playback paused.")
    else:
        await ctx.send("No audio is playing!")

@bot.command()
async def resume(ctx):
    """
    Command to resume playback.
    """
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Playback resumed.")
    else:
        await ctx.send("No audio is paused!")

# Run the bot
bot.run(DISCORD_TOKEN)
