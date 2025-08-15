# Discord Bot OAuth2 Django App

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file:**
   ```bash
   copy .env.example .env
   ```

3. **Configure Discord Application:**
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Go to OAuth2 settings
   - Add redirect URI: `http://localhost:8000/callback/`
   - Copy Client ID and Client Secret

4. **Update .env file:**
   ```
   DISCORD_CLIENT_ID=your_actual_client_id
   DISCORD_CLIENT_SECRET=your_actual_client_secret
   DISCORD_REDIRECT_URI=http://localhost:8000/callback/
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start development server:**
   ```bash
   python manage.py runserver
   ```

7. **Test OAuth2 flow:**
   - Visit http://localhost:8000/
   - Click "Authorize Discord Bot"
   - Complete Discord authorization
   - You'll be redirected to callback with access token

## URLs
- `/` - Main page with authorization button
- `/callback/` - OAuth2 callback endpoint
- `/admin/` - Django admin panel