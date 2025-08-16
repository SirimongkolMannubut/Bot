# 🎨 NSFW Discord Bot with Realistic Vision AI

A powerful Discord bot that generates photorealistic images using Realistic Vision v5.1 model with role-based quota system.

## ✨ Features

- **🎨 Photorealistic Image Generation** - Uses Realistic Vision v5.1 for ultra-realistic results
- **🔞 NSFW Support** - Dedicated NSFW commands for adult content (NSFW channels only)
- **👑 Role-Based Quotas** - Admins get unlimited usage, regular users get 10 images/day
- **⚡ Fast Generation** - Optimized settings for quick results (1-2 minutes)
- **🔄 Fallback System** - Multiple APIs ensure reliability
- **💬 Dual Commands** - Both text commands (!) and slash commands (/)

## 🚀 Commands

### Text Commands
- `!nsfw <prompt>` - Generate NSFW images (NSFW channels only)
- `!image <prompt>` - Generate regular images
- `!gen <prompt>` - Generate regular images (alias)
- `!quota` - Check your daily quota
- `!ping` - Test bot status

### Slash Commands
- `/nsfw prompt:<text>` - Generate NSFW images
- `/gen prompt:<text>` - Generate regular images

## 🛠️ Setup

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd discordbot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
cp .env.example .env
```

Edit `.env` file:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### 4. Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Go to Bot section
4. Copy bot token to `.env` file
5. Enable required intents:
   - Message Content Intent
   - Server Members Intent

### 5. Run Bot
```bash
python nsfw_bot.py
```

## 🎯 AI Models

### Primary: Realistic Vision v5.1
- **Ultra-realistic** photographic results
- **High quality** skin textures and lighting
- **NSFW capable** with safety checker disabled

### Fallback: Pollinations API
- **Fast generation** when local model fails
- **No quotas** for basic functionality

## 👥 Role System

### Admin Roles
Users with these roles get **unlimited** image generation:
- `Admin`
- `Administrator` 
- `Mod`
- `Moderator`

### Regular Users
- **10 images per day**
- Quota resets at midnight
- Check quota with `!quota`

## 🔧 Technical Details

### Performance Optimizations
- **Async execution** - Non-blocking image generation
- **Thread isolation** - Prevents Discord heartbeat issues
- **Memory optimization** - Low CPU memory usage
- **Fast settings** - 15 steps, 6.0 guidance scale

### File Structure
```
discordbot/
├── nsfw_bot.py          # Main bot file
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 📋 Requirements

### Python Packages
- `discord.py` - Discord API wrapper
- `diffusers` - Hugging Face diffusion models
- `torch` - PyTorch for AI models
- `requests` - HTTP requests
- `python-dotenv` - Environment variables

### System Requirements
- **Python 3.8+**
- **4GB+ RAM** (8GB+ recommended)
- **GPU optional** (CUDA for faster generation)
- **Internet connection** for model downloads

## 🔒 Security Features

- **Environment variables** for sensitive data
- **Role-based access control**
- **NSFW channel restrictions**
- **Rate limiting** with daily quotas
- **Safe model loading** with error handling

## 🚨 Important Notes

### Model Files
- Models are **NOT included** in repository (too large)
- First run will **download models automatically**
- Realistic Vision v5.1: ~4GB download
- Models stored in `models/` directory

### NSFW Content
- NSFW commands **only work in NSFW channels**
- Safety checker is **disabled** for realistic results
- Use responsibly and follow Discord ToS

### Performance
- **CPU generation**: 1-2 minutes per image
- **GPU generation**: 10-30 seconds per image
- Bot remains responsive during generation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is for educational purposes. Please use responsibly and follow all applicable laws and Discord Terms of Service.

## ⚠️ Disclaimer

This bot generates AI images and may produce unexpected results. Users are responsible for their usage and ensuring compliance with local laws and platform policies.