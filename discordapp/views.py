from django.http import HttpResponse
from django.shortcuts import render
from requests import post, get
from os import getenv
import html
import json

def index(request):
    context = {
        'client_id': getenv('DISCORD_CLIENT_ID', '1405862446295552040'),
        'redirect_uri': getenv('DISCORD_REDIRECT_URI', 'https://bot-sb53.onrender.com/callback/')
    }
    return render(request, 'discordapp/index.html', context)

def discord_callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse("No code provided", status=400)

    data = {
        'client_id': getenv('DISCORD_CLIENT_ID', '1405862446295552040'),
        'client_secret': getenv('DISCORD_CLIENT_SECRET', 'XaJ6KmP9R9SmgA5fdtKYrrx-zeqhUpna'),
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': getenv('DISCORD_REDIRECT_URI', 'https://bot-sb53.onrender.com/callback/'),
        'scope': 'bot applications.commands'
    }

    try:
        response = post('https://discord.com/api/oauth2/token', data=data)
        
        if response.status_code == 200:
            try:
                token_info = response.json()
                access_token = token_info.get('access_token')
                
                if access_token:
                    # Get user info from Discord API
                    headers = {"Authorization": f"Bearer {access_token}"}
                    user_response = get("https://discord.com/api/users/@me", headers=headers)
                    
                    if user_response.status_code == 200:
                        user_info = user_response.json()
                        username = html.escape(user_info.get('username', 'Unknown'))
                        user_id = html.escape(str(user_info.get('id', 'Unknown')))
                        return HttpResponse(f"Success! User: {username} (ID: {user_id})")
                    else:
                        return HttpResponse(f"Token valid but failed to get user info: {user_response.status_code}")
                else:
                    return HttpResponse("No access token received")
            except json.JSONDecodeError:
                return HttpResponse("Invalid JSON response from Discord API", status=500)
        else:
            try:
                error_info = response.json()
                error_msg = html.escape(str(error_info))
                return HttpResponse(f"Error: {error_msg}", status=400)
            except json.JSONDecodeError:
                return HttpResponse(f"HTTP Error: {response.status_code}", status=400)
    except Exception as e:
        error_msg = html.escape(str(e))
        return HttpResponse(f"Request failed: {error_msg}", status=500)
