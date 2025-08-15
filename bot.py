import discord
from discord.ext import commands
from os import getenv
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # ต้องเปิดเพื่ออ่านข้อความ

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Bot is ready and connected to {len(bot.guilds)} servers')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")