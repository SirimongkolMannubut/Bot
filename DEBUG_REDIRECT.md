# Debug Redirect URI Issue

## Current URLs in Code:
- Authorization: `https://discord.com/oauth2/authorize?client_id=1405862446295552040&permissions=68608&response_type=code&redirect_uri=https://bot-sb53.onrender.com/callback/&integration_type=0&scope=bot%20applications.commands`
- Token Exchange: `https://bot-sb53.onrender.com/callback/`

## Fix Steps:

### 1. Discord Developer Portal
Go to: https://discord.com/developers/applications/1405862446295552040/oauth2

**Add EXACT redirect URI:**
```
https://bot-sb53.onrender.com/callback/
```

### 2. Check Current Registered URIs
Make sure these are registered:
- `https://bot-sb53.onrender.com/callback/`
- `http://127.0.0.1:8000/callback/` (for local dev)

### 3. URL Encoding
Discord is strict about URL matching. Make sure no extra characters.

## Test URLs:
- Production: https://bot-sb53.onrender.com/
- Local: http://127.0.0.1:8000/