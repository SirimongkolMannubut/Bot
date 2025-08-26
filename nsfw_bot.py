import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
import urllib.parse
import json
from datetime import datetime
import tempfile
import asyncio

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

is_generating = False
pipe = None

# โหลด Local Model (สมจริงกว่า)
def load_local_model():
    global pipe
    try:
        from diffusers import StableDiffusionPipeline
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        print(f"Loading Realistic Vision v5.1 model on {device} with {dtype}... (this may take a while)")
        
        # ใช้ Realistic Vision v5.1 (สมจริงกว่า SD v1.5) - ปรับให้เร็วกว่า
        pipe = StableDiffusionPipeline.from_pretrained(
            "SG161222/Realistic_Vision_V5.1_noVAE",
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        pipe.to(device)
        pipe.safety_checker = None  # ปิด safety checker สำหรับ NSFW
        
        # เพิ่ม scheduler เร็วขึ้น
        from diffusers import DPMSolverMultistepScheduler
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        
        print("[SUCCESS] Realistic Vision v5.1 model loaded successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load Realistic Vision v5.1: {e}")
        return False

# โหลดข้อมูลโควต้า
def load_usage():
    try:
        with open('usage.json', 'r') as f:
            return json.load(f)
    except:
        return {}

# บันทึกข้อมูลโควต้า
def save_usage(usage_data):
    with open('usage.json', 'w') as f:
        json.dump(usage_data, f)

# เช็คโควต้า
def check_quota(user_id, member):
    usage = load_usage()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # เช็ค Role Admin
    is_admin = any(role.name.lower() in ['admin', 'administrator', 'mod', 'moderator'] for role in member.roles)
    
    if is_admin:
        return True, 0, "unlimited"
    
    # เช็คโควต้าคนทั่วไป
    user_id = str(user_id)
    if user_id not in usage:
        usage[user_id] = {}
    
    if today not in usage[user_id]:
        usage[user_id][today] = 0
    
    current_count = usage[user_id][today]
    
    if current_count >= 10:
        return False, current_count, 10
    
    # เพิ่มการใช้งาน
    usage[user_id][today] += 1
    save_usage(usage)
    
    return True, usage[user_id][today], 10

# ฟังก์ชันสร้างภาพแบบเดียวกัน
async def generate_image(prompt, is_nsfw=False):
    if not pipe:
        return None, "❌ โมเดล Realistic Vision v5.1 ไม่พร้อมใช้งาน!"
    
    try:
        # เพิ่ม prompt สำหรับความสมจริงสูงสุด
        enhanced_prompt = f"{prompt}, ultra photorealistic, hyperrealistic, 8k uhd, professional photography, realistic lighting, depth of field, sharp focus, detailed textures, lifelike, high detail, cinematic lighting, studio quality"
        
        negative_prompt = "cartoon, anime, illustration, painting, drawing, fake, artificial, stylized, unrealistic, plastic, low quality, blurry, deformed, distorted"
        
        print(f"Generating MAXIMUM realistic image: {enhanced_prompt}")
        
        # รันใน thread แยกเพื่อไม่ block Discord
        loop = asyncio.get_event_loop()
        def generate():
            return pipe(
                enhanced_prompt, 
                negative_prompt=negative_prompt, 
                height=768, 
                width=512, 
                num_inference_steps=50,  # เพิ่มขึ้นเพื่อความละเอียด
                guidance_scale=8.5,      # เพิ่มเพื่อให้ตาม prompt มากขึ้น
                num_images_per_prompt=1,
                eta=0.0                  # ลดความสุ่มเพื่อความสมจริง
            ).images[0]
        
        image = await loop.run_in_executor(None, generate)
        
        # บันทึกและส่งไฟล์
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            file_path = tmp.name
        image.save(file_path)
        
        filename = "nsfw.png" if is_nsfw else "image.png"
        file = discord.File(file_path, filename=filename)
        
        return file, file_path
        
    except Exception as e:
        print(f"Local model error: {e}")
        return None, "❌ Local AI ล้มเหลว! กรุณาตรวจสอบโมเดล Realistic Vision v5.1"

@bot.event
async def on_ready():
    print(f"NSFW Bot ready: {bot.user}")
    
    # โหลด Local Model
    success = load_local_model()
    if success:
        print("[INFO] Realistic Vision v5.1 ready - maximum realism mode!")
    else:
        print("[ERROR] Realistic Vision v5.1 failed - bot will not work without it!")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.command()
async def nsfw(ctx, *, prompt: str):
    global is_generating
    
    if not ctx.channel.is_nsfw():
        await ctx.send("⚠️ ใช้ได้เฉพาะช่อง NSFW!")
        return
    
    # เช็คโควต้า
    can_use, current_count, max_count = check_quota(ctx.author.id, ctx.author)
    if not can_use:
        await ctx.send(f"❌ คุณใช้โควต้าครบ {max_count} รูปแล้วสำหรับวันนี้! รอพรุ่งนี้นะ")
        return
    
    if is_generating:
        await ctx.send("⏳ รอสักครู่...")
        return
    
    is_generating = True
    
    try:
        msg = await ctx.send("🎨 กำลังสร้างภาพสมจริงสูงสุด! ด้วย AI... (ใช้เวลา 6-10 นาที - 50 steps สมจริงสูงสุด!)")
        
        file, result = await generate_image(prompt, is_nsfw=True)
        
        if file:
            quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
            await msg.edit(content=f"🎨 ผลลัพธ์ 768x512 (50 STEPS - สมจริงสูงสุด!): {prompt}{quota_text}")
            await ctx.send(file=file)
            os.remove(result)
            print("[SUCCESS] MAXIMUM realistic image generation successful!")
        else:
            await msg.edit(content=result)
        
    except Exception as e:
        await ctx.send(f"❌ ผิดพลาด: {e}")
    finally:
        is_generating = False

@bot.command()
async def image(ctx, *, prompt: str):
    global is_generating
    
    # เช็คโควต้า
    can_use, current_count, max_count = check_quota(ctx.author.id, ctx.author)
    if not can_use:
        await ctx.send(f"❌ คุณใช้โควต้าครบ {max_count} รูปแล้วสำหรับวันนี้! รอพรุ่งนี้นะ")
        return
    
    if is_generating:
        await ctx.send("⏳ รอสักครู่...")
        return
    
    is_generating = True
    
    try:
        msg = await ctx.send("🎨 กำลังสร้างภาพสมจริงสูงสุด! ด้วย AI... (ใช้เวลา 6-10 นาที - 50 steps สมจริงสูงสุด!)")
        
        file, result = await generate_image(prompt, is_nsfw=False)
        
        if file:
            quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
            await msg.edit(content=f"🎨 ผลลัพธ์ 768x512 (50 STEPS - สมจริงสูงสุด!): {prompt}{quota_text}")
            await ctx.send(file=file)
            os.remove(result)
            print("[SUCCESS] MAXIMUM realistic image generation successful!")
        else:
            await msg.edit(content=result)
        
    except Exception as e:
        await ctx.send(f"❌ ผิดพลาด: {e}")
    finally:
        is_generating = False

@bot.command()
async def gen(ctx, *, prompt: str):
    await image(ctx, prompt=prompt)

@bot.tree.command(name="nsfw", description="Generate NSFW images (NSFW channels only)")
async def slash_nsfw(interaction: discord.Interaction, prompt: str):
    if not interaction.channel.is_nsfw():
        await interaction.response.send_message("⚠️ ใช้ได้เฉพาะช่อง NSFW!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    # เช็คโควต้า
    can_use, current_count, max_count = check_quota(interaction.user.id, interaction.user)
    if not can_use:
        await interaction.followup.send(f"❌ คุณใช้โควต้าครบ {max_count} รูปแล้วสำหรับวันนี้! รอพรุ่งนี้นะ")
        return
    
    global is_generating
    if is_generating:
        await interaction.followup.send("⏳ รอสักครู่...")
        return
    
    is_generating = True
    
    try:
        await interaction.followup.send("🎨 กำลังสร้างภาพสมจริงสูงสุด! ด้วย AI... (ใช้เวลา 6-10 นาที - 50 steps สมจริงสูงสุด!)")
        
        file, result = await generate_image(prompt, is_nsfw=True)
        
        if file:
            quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
            await interaction.followup.send(content=f"🎨 ผลลัพธ์ 768x512 (50 STEPS - สมจริงสูงสุด!): {prompt}{quota_text}", file=file)
            os.remove(result)
        else:
            await interaction.followup.send(result)
            
    except Exception as e:
        await interaction.followup.send(f"❌ ผิดพลาด: {e}")
    finally:
        is_generating = False

@bot.tree.command(name="gen", description="Generate regular images")
async def slash_gen(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    
    # เช็คโควต้า
    can_use, current_count, max_count = check_quota(interaction.user.id, interaction.user)
    if not can_use:
        await interaction.followup.send(f"❌ คุณใช้โควต้าครบ {max_count} รูปแล้วสำหรับวันนี้! รอพรุ่งนี้นะ")
        return
    
    global is_generating
    if is_generating:
        await interaction.followup.send("⏳ รอสักครู่...")
        return
    
    is_generating = True
    
    try:
        await interaction.followup.send("🎨 กำลังสร้างภาพสมจริงสูงสุด! ด้วย AI... (ใช้เวลา 6-10 นาที - 50 steps สมจริงสูงสุด!)")
        
        file, result = await generate_image(prompt, is_nsfw=False)
        
        if file:
            quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
            await interaction.followup.send(content=f"🎨 ผลลัพธ์ 768x512 (50 STEPS - สมจริงสูงสุด!): {prompt}{quota_text}", file=file)
            os.remove(result)
        else:
            await interaction.followup.send(result)
            
    except Exception as e:
        await interaction.followup.send(f"❌ ผิดพลาด: {e}")
    finally:
        is_generating = False

@bot.command()
async def quota(ctx):
    usage = load_usage()
    today = datetime.now().strftime('%Y-%m-%d')
    
    is_admin = any(role.name.lower() in ['admin', 'administrator', 'mod', 'moderator'] for role in ctx.author.roles)
    
    if is_admin:
        await ctx.send("👑 Admin - ไม่จำกัดการใช้งาน!")
    else:
        user_id = str(ctx.author.id)
        current_count = usage.get(user_id, {}).get(today, 0)
        await ctx.send(f"📊 โควต้าวันนี้: {current_count}/10 รูป")

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    model_status = "✅ Realistic Vision v5.1" if pipe else "❌ ไม่พร้อม"
    await ctx.send(f"🏓 Pong! {latency}ms\n🤖 AI: {model_status}")

if __name__ == "__main__":
    bot.run(TOKEN)