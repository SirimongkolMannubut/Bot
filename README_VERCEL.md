# Deploy to Vercel

## Quick Setup

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Vercel:**
   - Go to https://vercel.com
   - Import your GitHub repository
   - Add environment variables:
     - `DISCORD_CLIENT_ID`
     - `DISCORD_CLIENT_SECRET`
     - `DISCORD_REDIRECT_URI` (https://yourapp.vercel.app/callback/)
     - `SECRET_KEY`
     - `DEBUG=False`

3. **Update Discord App:**
   - Go to Discord Developer Portal
   - Update redirect URI to: `https://yourapp.vercel.app/callback/`

## Environment Variables Required:
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_REDIRECT_URI`
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=.vercel.app`