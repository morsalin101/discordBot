import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the bot token from .env
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()  # Default intents (no member events, etc.)
intents.message_content = True      # Required to read message content

# Define the bot with intents
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, World!")

@bot.command()
async def help(ctx):
        help_text = """
        **Available Commands:**
        `!hello` - Greets the user.
        `!help` - Shows this help message.
        """
        await ctx.send(help_text)
  

# Run the bot
bot.run(TOKEN)
