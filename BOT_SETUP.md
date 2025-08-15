# Discord Bot Setup Guide

## 1. Get Bot Token

1. Go to Discord Developer Portal: https://discord.com/developers/applications/1405862446295552040
2. Go to **Bot** section
3. Copy **Token** (Reset if needed)
4. Add to `.env` file:
   ```
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   ```

## 2. Bot Permissions URL

Use this URL to add bot to server:
```
https://discord.com/oauth2/authorize?client_id=1405862446295552040&permissions=68608&scope=bot%20applications.commands
```

## 3. Run Bot Locally

```bash
pip install discord.py
python bot.py
```

## 4. Test Commands

In Discord server:
- `!ping` → Bot replies "Pong!"
- `!hello` → Bot says hello

## 5. Bot Features

- ✅ OAuth2 web interface
- ✅ User authentication
- ✅ Basic bot commands
- ✅ Environment variables
- ✅ Ready for deployment