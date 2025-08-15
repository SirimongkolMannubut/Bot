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
intents.members = True
intents.guilds = True

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
    msg = None
    
    try:
        loading_msg = f"⏳ กำลังสร้างภาพ: `{prompt}` ..."
        if ctx:
            msg = await ctx.send(loading_msg)
        elif interaction:
            await interaction.response.send_message(loading_msg)
        
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        embed = discord.Embed(title=f"🎨 ผลลัพธ์: {prompt}", color=discord.Color.green())
        embed.set_image(url=image_url)
        
        if ctx and msg:
            await msg.edit(content="", embed=embed)
        elif interaction:
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        error_msg = f"❌ เกิดข้อผิดพลาด: {str(e)}"
        if ctx and msg:
            await msg.edit(content=error_msg)
        elif ctx:
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

# Member join event
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="🎉 สมาชิกใหม่!", 
            description=f"{member.mention} เข้าร่วมเซิร์ฟเวอร์!", 
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ชื่อ", value=member.name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        await channel.send(embed=embed)

# Member leave event
@bot.event
async def on_member_remove(member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="👋 ลาก่อน", 
            description=f"{member.name} ออกจากเซิร์ฟเวอร์!", 
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# Member update event (nickname changes)
@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        channel = after.guild.system_channel
        if channel:
            old_nick = before.nick or before.name
            new_nick = after.nick or after.name
            embed = discord.Embed(
                title="✏️ เปลี่ยนชื่อ", 
                description=f"{after.mention} เปลี่ยนชื่อแล้ว", 
                color=discord.Color.blue()
            )
            embed.add_field(name="ชื่อเดิม", value=old_nick, inline=True)
            embed.add_field(name="ชื่อใหม่", value=new_nick, inline=True)
            await channel.send(embed=embed)

# Message delete event
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return  # Ignore bot messages
    
    channel = message.channel
    embed = discord.Embed(
        title="🗑️ ข้อความถูกลบ", 
        description=f"ข้อความจาก {message.author.mention} ถูกลบ", 
        color=discord.Color.orange()
    )
    embed.add_field(name="เนื้อหา", value=message.content[:1000] if message.content else "ไม่มีข้อความ", inline=False)
    embed.add_field(name="ช่อง", value=channel.mention, inline=True)
    embed.set_footer(text=f"User ID: {message.author.id}")
    await channel.send(embed=embed)

# Message edit event
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return  # Ignore bot messages and non-content changes
    
    channel = after.channel
    embed = discord.Embed(
        title="✏️ ข้อความถูกแก้ไข", 
        description=f"{after.author.mention} แก้ไขข้อความ", 
        color=discord.Color.yellow()
    )
    embed.add_field(name="ก่อน", value=before.content[:500] if before.content else "ไม่มีข้อความ", inline=False)
    embed.add_field(name="หลัง", value=after.content[:500] if after.content else "ไม่มีข้อความ", inline=False)
    embed.add_field(name="ช่อง", value=channel.mention, inline=True)
    embed.set_footer(text=f"User ID: {after.author.id}")
    await channel.send(embed=embed)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")