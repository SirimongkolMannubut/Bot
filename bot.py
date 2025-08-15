import discord
from discord.ext import commands
from discord import app_commands
from os import getenv, environ
from dotenv import load_dotenv
import urllib.parse

# Set UTF-8 encoding for Windows compatibility
environ['PYTHONUTF8'] = '1'

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Prevent duplicate image generation
is_generating = False

@bot.event
async def on_ready():
    try:
        print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})".encode("utf-8", errors="ignore").decode())
        print(f"Bot is ready and connected to {len(bot.guilds)} servers".encode("utf-8", errors="ignore").decode())
    except UnicodeEncodeError:
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        print(f"Bot is ready and connected to {len(bot.guilds)} servers")
    
    try:
        synced = await bot.tree.sync()
        try:
            print(f"🔄 Synced {len(synced)} slash command(s)".encode("utf-8", errors="ignore").decode())
        except UnicodeEncodeError:
            print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        try:
            print(f"❌ Error syncing commands: {e}".encode("utf-8", errors="ignore").decode())
        except UnicodeEncodeError:
            print(f"Error syncing commands: {e}")

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

async def generate_image_once(prompt, ctx=None, interaction=None):
    global is_generating
    
    if is_generating:
        message = "⏳ รอให้บอทสร้างภาพเสร็จก่อนนะ"
        if ctx:
            await ctx.send(message)
        elif interaction:
            await interaction.response.send_message(message)
        return
    
    is_generating = True
    
    try:
        loading_msg = f"⏳ กำลังสร้างภาพ: `{prompt}` ..."
        if ctx:
            await ctx.send(loading_msg)
        elif interaction:
            await interaction.response.send_message(loading_msg)
        
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        embed = discord.Embed(title=f"🎨 ผลลัพธ์: {prompt}", color=discord.Color.green())
        embed.set_image(url=image_url)
        
        if ctx:
            await ctx.send(embed=embed)
        elif interaction:
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        error_msg = f"❌ เกิดข้อผิดพลาด: {str(e)}"
        if ctx:
            await ctx.send(error_msg)
        elif interaction:
            if interaction.response.is_done():
                await interaction.followup.send(error_msg)
            else:
                await interaction.response.send_message(error_msg)
    finally:
        is_generating = False

@bot.command()
async def image(ctx, *, prompt):
    await generate_image_once(prompt, ctx=ctx)

@bot.command()
async def draw(ctx, *, prompt):
    await generate_image_once(prompt, ctx=ctx)

@bot.tree.command(name="image", description="Generate an image from text prompt")
async def image_slash(interaction: discord.Interaction, prompt: str):
    await generate_image_once(prompt, interaction=interaction)

@bot.tree.command(name="draw", description="Draw an image using AI")
async def draw_slash(interaction: discord.Interaction, prompt: str):
    await generate_image_once(prompt, interaction=interaction)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")