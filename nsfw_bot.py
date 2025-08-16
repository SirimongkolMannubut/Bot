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
        
        print("[SUCCESS] Realistic Vision v5.1 model loaded successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load realistic model: {e}")
        print("Trying SD v1.5 fallback...")
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=dtype
            )
            pipe.to(device)
            pipe.safety_checker = None
            print("[SUCCESS] SD v1.5 fallback loaded!")
            return True
        except Exception as e2:
            print(f"[ERROR] All models failed: {e2}")
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

@bot.event
async def on_ready():
    print(f"NSFW Bot ready: {bot.user}")
    
    # โหลด Local Model
    success = load_local_model()
    if success:
        print("[INFO] Realistic AI ready - unlimited generation!")
    else:
        print("[WARNING] Local AI failed - using Pollinations fallback")
    
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
        msg = await ctx.send("🎨 กำลังสร้างภาพ...")
        
        # ใช้ Local AI (สมจริงกว่า)
        if pipe:
            try:
                await msg.edit(content="🎨 กำลังสร้างภาพสมจริงด้วย AI... (ใช้เวลา 1-2 นาที)")
                
                enhanced_prompt = f"{prompt}, photorealistic, ultra realistic, 8k, detailed skin texture, natural lighting, professional photography, hyperrealistic, lifelike, cinematic quality"
                print(f"Generating realistic image: {enhanced_prompt}")
                
                # รันใน thread แยกเพื่อไม่ block Discord - ปรับให้เร็วกว่า
                loop = asyncio.get_event_loop()
                def generate():
                    return pipe(enhanced_prompt, height=512, width=512, num_inference_steps=15, guidance_scale=6.0).images[0]
                image = await loop.run_in_executor(None, generate)
                
                # บันทึกและส่งไฟล์
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    file_path = tmp.name
                image.save(file_path)
                
                file = discord.File(file_path, filename="nsfw.png")
                quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
                await msg.edit(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}")
                await ctx.send(file=file)
                
                os.remove(file_path)
                print("[SUCCESS] Realistic image generation successful!")
                return
            except Exception as e:
                print(f"Local model error: {e}")
                await msg.edit(content="⚠️ Local AI ล้มเหลว ใช้ Pollinations แทน...")
        
        # Fallback ใช้ Pollinations
        clean_prompt = f"{prompt}, photorealistic, ultra realistic, detailed"
        encoded_prompt = urllib.parse.quote(clean_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Admin - ไม่จำกัด)"
        await msg.edit(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}\n{image_url}")
        
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
        msg = await ctx.send("🎨 กำลังสร้างภาพ...")
        
        # ใช้ Local AI (สมจริงกว่า)
        if pipe:
            try:
                await msg.edit(content="🎨 กำลังสร้างภาพสมจริงด้วย AI... (ใช้เวลา 1-2 นาที)")
                
                enhanced_prompt = f"{prompt}, photorealistic, ultra realistic, 8k, detailed, natural lighting, professional photography, hyperrealistic, lifelike, cinematic quality"
                print(f"Generating realistic image: {enhanced_prompt}")
                
                # รันใน thread แยกเพื่อไม่ block Discord - ปรับให้เร็วกว่า
                loop = asyncio.get_event_loop()
                def generate():
                    return pipe(enhanced_prompt, height=512, width=512, num_inference_steps=15, guidance_scale=6.0).images[0]
                image = await loop.run_in_executor(None, generate)
                
                # บันทึกและส่งไฟล์
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    file_path = tmp.name
                image.save(file_path)
                
                file = discord.File(file_path, filename="image.png")
                quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
                await msg.edit(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}")
                await ctx.send(file=file)
                
                os.remove(file_path)
                print("[SUCCESS] Realistic image generation successful!")
                return
            except Exception as e:
                print(f"Local model error: {e}")
                await msg.edit(content="⚠️ Local AI ล้มเหลว ใช้ Pollinations แทน...")
        
        # Fallback ใช้ Pollinations
        encoded_prompt = urllib.parse.quote(f"{prompt}, photorealistic, ultra realistic, detailed")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Admin - ไม่จำกัด)"
        await msg.edit(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}\n{image_url}")
        
    except Exception as e:
        await ctx.send(f"❌ ผิดพลาด: {e}")
    finally:
        is_generating = False

@bot.command()
async def quota(ctx):
    usage = load_usage()
    today = datetime.now().strftime('%Y-%m-%d')
    user_id = str(ctx.author.id)
    
    # เช็ค Role Admin
    is_admin = any(role.name.lower() in ['admin', 'administrator', 'mod', 'moderator'] for role in ctx.author.roles)
    
    if is_admin:
        await ctx.send("👑 คุณเป็น Admin - ไม่มีข้อจำกัดการใช้งาน!")
        return
    
    current_count = usage.get(user_id, {}).get(today, 0)
    await ctx.send(f"📊 โควต้าวันนี้: {current_count}/10 รูป\n⏰ รีเซ็ตเที่ยงคืน")

@bot.command()
async def ping(ctx):
    status = "[SUCCESS] Realistic AI ready!" if pipe else "[ERROR] Local AI not ready"
    await ctx.send(f"Pong! 🏓\n{status}")

# เพิ่ม prefix commands กลับมา
@bot.command(name="gen")
async def gen_prefix(ctx, *, prompt: str):
    # เหมือนกับ !image
    await image(ctx, prompt=prompt)

# Slash Commands
@bot.tree.command(name="gen", description="สร้างภาพ AI สมจริง")
async def gen_slash(interaction: discord.Interaction, prompt: str):
    global is_generating
    
    # เช็คโควต้า
    can_use, current_count, max_count = check_quota(interaction.user.id, interaction.user)
    if not can_use:
        await interaction.response.send_message(f"❌ คุณใช้โควต้าครบ {max_count} รูปแล้ว! รอพรุ่งนี้", ephemeral=True)
        return
    
    if is_generating:
        await interaction.response.send_message("⏳ รอสักครู่...", ephemeral=True)
        return
    
    is_generating = True
    
    try:
        await interaction.response.send_message("🎨 กำลังสร้างภาพ...")
        
        # ใช้ Local AI
        if pipe:
            try:
                await interaction.edit_original_response(content="🎨 กำลังสร้างภาพสมจริงด้วย AI... (ใช้เวลา 1-2 นาที)")
                
                enhanced_prompt = f"{prompt}, photorealistic, ultra realistic, 8k, detailed, natural lighting, professional photography, hyperrealistic, lifelike, cinematic quality"
                
                loop = asyncio.get_event_loop()
                def generate():
                    return pipe(enhanced_prompt, height=512, width=512, num_inference_steps=15, guidance_scale=6.0).images[0]
                image = await loop.run_in_executor(None, generate)
                
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    file_path = tmp.name
                image.save(file_path)
                
                file = discord.File(file_path, filename="generated.png")
                quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
                await interaction.edit_original_response(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}")
                await interaction.followup.send(file=file)
                
                os.remove(file_path)
                return
            except Exception as e:
                print(f"Local model error: {e}")
        
        # Fallback Pollinations
        encoded_prompt = urllib.parse.quote(f"{prompt}, photorealistic, ultra realistic, detailed")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Admin - ไม่จำกัด)"
        await interaction.edit_original_response(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}\n{image_url}")
        
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ ผิดพลาด: {e}")
    finally:
        is_generating = False

@bot.tree.command(name="nsfw", description="สร้างภาพ NSFW สมจริง (เฉพาะช่อง NSFW)")
async def nsfw_slash(interaction: discord.Interaction, prompt: str):
    if not interaction.channel.is_nsfw():
        await interaction.response.send_message("⚠️ ใช้ได้เฉพาะช่อง NSFW!", ephemeral=True)
        return
    
    global is_generating
    
    # เช็คโควต้า
    can_use, current_count, max_count = check_quota(interaction.user.id, interaction.user)
    if not can_use:
        await interaction.response.send_message(f"❌ คุณใช้โควต้าครบ {max_count} รูปแล้ว! รอพรุ่งนี้", ephemeral=True)
        return
    
    if is_generating:
        await interaction.response.send_message("⏳ รอสักครู่...", ephemeral=True)
        return
    
    is_generating = True
    
    try:
        await interaction.response.send_message("🎨 กำลังสร้างภาพ...")
        
        # ใช้ Local AI
        if pipe:
            try:
                await interaction.edit_original_response(content="🎨 กำลังสร้างภาพสมจริงด้วย AI... (ใช้เวลา 1-2 นาที)")
                
                enhanced_prompt = f"{prompt}, photorealistic, ultra realistic, 8k, detailed skin texture, natural lighting, professional photography, hyperrealistic, lifelike, cinematic quality"
                
                loop = asyncio.get_event_loop()
                def generate():
                    return pipe(enhanced_prompt, height=512, width=512, num_inference_steps=15, guidance_scale=6.0).images[0]
                image = await loop.run_in_executor(None, generate)
                
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    file_path = tmp.name
                image.save(file_path)
                
                file = discord.File(file_path, filename="nsfw.png")
                quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Realistic AI - ไม่จำกัด)"
                await interaction.edit_original_response(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}")
                await interaction.followup.send(file=file)
                
                os.remove(file_path)
                return
            except Exception as e:
                print(f"Local model error: {e}")
        
        # Fallback Pollinations
        clean_prompt = f"{prompt}, photorealistic, ultra realistic, detailed"
        encoded_prompt = urllib.parse.quote(clean_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        quota_text = f" ({current_count}/{max_count} รูป)" if max_count != "unlimited" else " (Admin - ไม่จำกัด)"
        await interaction.edit_original_response(content=f"🎨 ผลลัพธ์: {prompt}{quota_text}\n{image_url}")
        
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ ผิดพลาด: {e}")
    finally:
        is_generating = False

if __name__ == "__main__":
    bot.run(TOKEN)