import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
from dotenv import load_dotenv
import openai

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')
OPENAI_API_KEY = getenv('OPENAI_API_KEY')

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

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

@bot.command()
async def image(ctx, *, prompt):
    if not OPENAI_API_KEY:
        await ctx.send("❌ OpenAI API key not configured")
        return
    
    await ctx.send(f"⏳ กำลังสร้างภาพ: `{prompt}` ...")
    try:
        response = openai.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="512x512",
            n=1
        )
        image_url = response.data[0].url
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

@bot.tree.command(name="image", description="Generate an image from text prompt")
async def image_slash(interaction: discord.Interaction, prompt: str):
    if not OPENAI_API_KEY:
        await interaction.response.send_message("❌ OpenAI API key not configured")
        return
    
    await interaction.response.send_message(f"⏳ กำลังสร้างภาพ: `{prompt}` ...")
    try:
        response = openai.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="512x512",
            n=1
        )
        image_url = response.data[0].url
        await interaction.followup.send(image_url)
    except Exception as e:
        await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")