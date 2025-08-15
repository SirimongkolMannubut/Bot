import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Bot is ready and connected to {len(bot.guilds)} servers')
    try:
        synced = await bot.tree.sync()
        print(f'🔄 Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'❌ Error syncing commands: {e}')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.name}!")

@bot.tree.command(name="ping", description="Check if bot is responsive")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")