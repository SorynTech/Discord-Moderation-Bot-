import os
import discord
from discord import app_commands, Member
from discord.ext import commands
import datetime
import requests
import random as r
from aiohttp import web
import logging

# Track bot start time for uptime
bot_start_time = None
if bot_start_time is None:
    bot_start_time = datetime.datetime.now()

# Track update status
bot_updating = False
# Track emergency shutdown status
bot_emergency_shutdown = False
# Track owner sleep status
bot_owner_sleeping = False
# End Initalization



# Create handler
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True  # Add this line
bot = commands.Bot(command_prefix='!', intents=intents)


def load_env_file(filepath='.env'):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip().strip('"').strip("'")
                    os.environ[key.strip()] = value


load_env_file()

TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT = os.getenv('DISCORD_CLIENT_ID')
URL = os.getenv('DISCORD_BOT_URL')
PORT = os.getenv('PORT', 10000)

if TOKEN:
    print("Token Found")
else:
    print("Token not found")
if CLIENT:
    print("Client found")
else:
    print("Client not found")
if URL:
    print("URL found")
    print(URL)
else:
    print("URL not found")


async def health_check(request):
    global bot_updating, bot_emergency_shutdown, bot_owner_sleeping

    if bot_start_time is None:
        return web.Response(
            text="Bot is starting up, please wait...",
            content_type='text/plain',
            status=503
        )

    # Check if bot is in emergency shutdown mode
    if bot_emergency_shutdown:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Discord Bot Status</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(180deg, #001220 0%, #003d5c 50%, #001a2e 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                    position: relative;
                    overflow: hidden;
                }
                body::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: 
                        radial-gradient(ellipse at 20% 30%, rgba(0, 150, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(ellipse at 80% 70%, rgba(0, 100, 180, 0.1) 0%, transparent 50%);
                    animation: waterMovement 8s ease-in-out infinite;
                }
                @keyframes waterMovement {
                    0%, 100% { opacity: 0.3; }
                    50% { opacity: 0.6; }
                }
                .bubbles {
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    pointer-events: none;
                }
                .bubble {
                    position: absolute;
                    bottom: -100px;
                    width: 15px;
                    height: 15px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 50%;
                    animation: rise 8s infinite ease-in;
                }
                .bubble:nth-child(1) { left: 10%; animation-delay: 0s; width: 10px; height: 10px; }
                .bubble:nth-child(2) { left: 30%; animation-delay: 2s; width: 20px; height: 20px; }
                .bubble:nth-child(3) { left: 50%; animation-delay: 4s; width: 15px; height: 15px; }
                .bubble:nth-child(4) { left: 70%; animation-delay: 1s; width: 12px; height: 12px; }
                .bubble:nth-child(5) { left: 90%; animation-delay: 3s; width: 18px; height: 18px; }
                @keyframes rise {
                    to { bottom: 110%; opacity: 0; }
                }
                .container {
                    background: rgba(0, 30, 50, 0.9);
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 0 40px rgba(0, 150, 255, 0.1);
                    padding: 40px;
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                    position: relative;
                    z-index: 10;
                    border: 2px solid rgba(0, 150, 255, 0.2);
                }
                .status-icon {
                    width: 100px;
                    height: 100px;
                    background: linear-gradient(135deg, #1a5490 0%, #0d2a45 100%);
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0 auto 20px;
                    border: 3px solid rgba(255, 0, 0, 0.5);
                    position: relative;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0%, 100% { box-shadow: 0 0 20px rgba(255, 0, 0, 0.5); }
                    50% { box-shadow: 0 0 40px rgba(255, 0, 0, 0.8); }
                }
                .shark-icon {
                    font-size: 50px;
                }
                h1 {
                    color: #e0f7ff;
                    margin-bottom: 10px;
                    font-size: 28px;
                    text-shadow: 0 0 10px rgba(0, 150, 255, 0.5);
                }
                .status {
                    color: #ff4444;
                    font-weight: bold;
                    font-size: 18px;
                    margin-bottom: 30px;
                    text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
                }
                .info-message {
                    background: rgba(255, 68, 68, 0.1);
                    border-left: 4px solid #ff4444;
                    padding: 15px;
                    border-radius: 5px;
                    color: #ffaaaa;
                    margin-top: 20px;
                }
                .github-button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: rgba(36, 41, 47, 0.9);
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 8px;
                    border: 2px solid rgba(100, 180, 220, 0.3);
                    transition: all 0.3s ease;
                    font-weight: 500;
                }
                .github-button:hover {
                    background: rgba(48, 54, 61, 1);
                    border-color: rgba(100, 180, 220, 0.6);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }
                @media (max-width: 480px) {
                    .container {
                        padding: 30px 20px;
                    }
                    h1 {
                        font-size: 24px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="bubbles">
                <div class="bubble"></div>
                <div class="bubble"></div>
                <div class="bubble"></div>
                <div class="bubble"></div>
                <div class="bubble"></div>
            </div>
            <div class="container">
                <div class="status-icon">
                    <span class="shark-icon">🦈</span>
                </div>
                <h1>Shark Bot is <span class="status">Offline</span></h1>
                <p style="color: #7eb8d6; margin-bottom: 20px;">Shark in the deep waters</p>
                <div class="info-message">
                    🔴 The bot has gone into the deep. Emergency shutdown activated. Please check back later.
                </div>
                <a href="https://github.com/soryntech/discord-moderation-bot" target="_blank" class="github-button">
                    🔗 View on GitHub
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html', status=503)

    # Check if owner is sleeping
    if bot_owner_sleeping:
        uptime = datetime.datetime.now() - bot_start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Discord Bot Status</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(180deg, #003366 0%, #006699 50%, #003366 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                    position: relative;
                    overflow: hidden;
                }}
                body::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: 
                        radial-gradient(ellipse at 30% 30%, rgba(0, 200, 255, 0.15) 0%, transparent 50%),
                        radial-gradient(ellipse at 70% 70%, rgba(0, 150, 200, 0.15) 0%, transparent 50%);
                    animation: oceanWaves 10s ease-in-out infinite;
                }}
                @keyframes oceanWaves {{
                    0%, 100% {{ opacity: 0.5; }}
                    50% {{ opacity: 0.8; }}
                }}
                .fish {{
                    position: absolute;
                    font-size: 25px;
                    opacity: 0.4;
                    animation: fishSwim 15s linear infinite;
                }}
                .fish:nth-child(1) {{ top: 20%; animation-delay: 0s; }}
                .fish:nth-child(2) {{ top: 50%; animation-delay: 5s; }}
                .fish:nth-child(3) {{ top: 80%; animation-delay: 10s; }}
                @keyframes fishSwim {{
                    0% {{ left: -100px; transform: scaleX(1); }}
                    48% {{ transform: scaleX(1); }}
                    52% {{ transform: scaleX(-1); }}
                    100% {{ left: 110%; transform: scaleX(-1); }}
                }}
                .container {{
                    background: rgba(0, 60, 100, 0.9);
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 0 40px rgba(0, 200, 255, 0.1);
                    padding: 40px;
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                    position: relative;
                    z-index: 10;
                    border: 2px solid rgba(0, 200, 255, 0.3);
                }}
                .status-icon {{
                    width: 100px;
                    height: 100px;
                    background: linear-gradient(135deg, #00cc88 0%, #008855 100%);
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0 auto 20px;
                    animation: pulse 2s infinite;
                    border: 3px solid rgba(0, 204, 136, 0.5);
                }}
                @keyframes pulse {{
                    0%, 100% {{
                        transform: scale(1);
                        box-shadow: 0 0 20px rgba(0, 204, 136, 0.5);
                    }}
                    50% {{
                        transform: scale(1.05);
                        box-shadow: 0 0 40px rgba(0, 204, 136, 0.8);
                    }}
                }}
                .shark-icon {{
                    font-size: 50px;
                }}
                h1 {{
                    color: #e0f7ff;
                    margin-bottom: 10px;
                    font-size: 28px;
                    text-shadow: 0 0 10px rgba(0, 200, 255, 0.5);
                }}
                .status {{
                    color: #00ff88;
                    font-weight: bold;
                    font-size: 18px;
                    margin-bottom: 30px;
                    text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
                }}
                .info-grid {{
                    display: grid;
                    gap: 15px;
                    margin-top: 30px;
                }}
                .info-item {{
                    background: rgba(0, 100, 150, 0.3);
                    padding: 15px;
                    border-radius: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border: 1px solid rgba(0, 200, 255, 0.2);
                }}
                .info-label {{
                    color: #7eb8d6;
                    font-weight: 500;
                }}
                .info-value {{
                    color: #e0f7ff;
                    font-weight: bold;
                }}
                .bot-name {{
                    color: #00ddff;
                    font-weight: bold;
                    text-shadow: 0 0 5px rgba(0, 221, 255, 0.5);
                }}
                .github-button {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: rgba(36, 41, 47, 0.9);
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 8px;
                    border: 2px solid rgba(100, 180, 220, 0.3);
                    transition: all 0.3s ease;
                    font-weight: 500;
                }}
                .github-button:hover {{
                    background: rgba(48, 54, 61, 1);
                    border-color: rgba(100, 180, 220, 0.6);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }}
                @media (max-width: 480px) {{
                    .container {{
                        padding: 30px 20px;
                    }}
                    h1 {{
                        font-size: 24px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="fish">🐠</div>
            <div class="fish">🐟</div>
            <div class="fish">🐡</div>
            <div class="container">
                <div class="status-icon">
                    <span class="shark-icon">🦈</span>
                </div>
                <h1>Shark Owner is <span class="status">Sleeping</span></h1>
                <p style="color: #7eb8d6; margin-bottom: 20px;">SorynTech is asleep and isn't looking at PRs on GitHub right now</p>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">🦈 Shark Name</span>
                        <span class="info-value bot-name">{bot.user.name if bot.user else "Loading..."}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">⏱️ Swim Time</span>
                        <span class="info-value">{hours}h {minutes}m {seconds}s</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🏝️ Ocean Territories</span>
                        <span class="info-value">{len(bot.guilds)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">📡 Sonar Ping</span>
                        <span class="info-value">{round(bot.latency * 1000)}ms</span>
                    </div>
                </div>
                <a href="https://github.com/soryntech/discord-moderation-bot" target="_blank" class="github-button">
                    🔗 View on GitHub
                </a>
            </div>
        </body>
        </html>
"""
        return web.Response(text=html, content_type='text/html', status=200)

    # Check if bot is in update mode
    if bot_updating:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Discord Bot Status</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(180deg, #001f3f 0%, #004d7a 50%, #001f3f 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                    position: relative;
                    overflow: hidden;
                }
                body::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: 
                        radial-gradient(ellipse at 25% 35%, rgba(255, 140, 0, 0.1) 0%, transparent 50%),
                        radial-gradient(ellipse at 75% 65%, rgba(255, 100, 0, 0.1) 0%, transparent 50%);
                    animation: maintenanceGlow 6s ease-in-out infinite;
                }
                @keyframes maintenanceGlow {
                    0%, 100% { opacity: 0.4; }
                    50% { opacity: 0.8; }
                }
                .shark-swim {
                    position: absolute;
                    font-size: 60px;
                    animation: sharkCrossing 12s linear infinite;
                    opacity: 0.3;
                }
                @keyframes sharkCrossing {
                    0% { left: -100px; }
                    100% { left: 110%; }
                }
                .container {
                    background: rgba(0, 45, 80, 0.9);
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 0 40px rgba(255, 140, 0, 0.1);
                    padding: 40px;
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                    position: relative;
                    z-index: 10;
                    border: 2px solid rgba(255, 140, 0, 0.3);
                }
                .status-icon {
                    width: 100px;
                    height: 100px;
                    background: linear-gradient(135deg, #ff8c00 0%, #cc6600 100%);
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0 auto 20px;
                    animation: spin 3s linear infinite;
                    border: 3px solid rgba(255, 140, 0, 0.5);
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .update-icon {
                    font-size: 50px;
                }
                h1 {
                    color: #e0f7ff;
                    margin-bottom: 10px;
                    font-size: 28px;
                    text-shadow: 0 0 10px rgba(255, 140, 0, 0.5);
                }
                .status {
                    color: #ff9933;
                    font-weight: bold;
                    font-size: 18px;
                    margin-bottom: 30px;
                    text-shadow: 0 0 10px rgba(255, 153, 51, 0.5);
                }
                .info-message {
                    background: rgba(255, 140, 0, 0.15);
                    border-left: 4px solid #ff8c00;
                    padding: 15px;
                    border-radius: 5px;
                    color: #ffcc99;
                    margin-top: 20px;
                }
                .github-button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: rgba(36, 41, 47, 0.9);
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 8px;
                    border: 2px solid rgba(100, 180, 220, 0.3);
                    transition: all 0.3s ease;
                    font-weight: 500;
                }
                .github-button:hover {
                    background: rgba(48, 54, 61, 1);
                    border-color: rgba(100, 180, 220, 0.6);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }
                @media (max-width: 480px) {
                    .container {
                        padding: 30px 20px;
                    }
                    h1 {
                        font-size: 24px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="shark-swim" style="top: 20%;">🦈</div>
            <div class="shark-swim" style="top: 60%; animation-delay: 6s;">🦈</div>
            <div class="container">
                <div class="status-icon">
                    <span class="update-icon">⚙️</span>
                </div>
                <h1>Shark Bot is <span class="status">Updating</span></h1>
                <p style="color: #7eb8d6; margin-bottom: 20px;">Maintenance dive in progress</p>
                <div class="info-message">
                    ⚠️ The shark is performing maintenance in the deep. Check back in a few minutes.
                </div>
                <a href="https://github.com/soryntech/discord-moderation-bot" target="_blank" class="github-button">
                    🔗 View on GitHub
                </a>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html', status=503)  # MOVED THIS LINE HERE

    # Normal status (bot is running)
    uptime = datetime.datetime.now() - bot_start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Discord Bot Status</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(180deg, #003366 0%, #006699 50%, #003366 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                position: relative;
                overflow: hidden;
            }}
            body::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(ellipse at 30% 30%, rgba(0, 200, 255, 0.15) 0%, transparent 50%),
                    radial-gradient(ellipse at 70% 70%, rgba(0, 150, 200, 0.15) 0%, transparent 50%);
                animation: oceanWaves 10s ease-in-out infinite;
            }}
            @keyframes oceanWaves {{
                0%, 100% {{ opacity: 0.5; }}
                50% {{ opacity: 0.8; }}
            }}
            .fish {{
                position: absolute;
                font-size: 25px;
                opacity: 0.4;
                animation: fishSwim 15s linear infinite;
            }}
            .fish:nth-child(1) {{ top: 20%; animation-delay: 0s; }}
            .fish:nth-child(2) {{ top: 50%; animation-delay: 5s; }}
            .fish:nth-child(3) {{ top: 80%; animation-delay: 10s; }}
            @keyframes fishSwim {{
                0% {{ left: -100px; transform: scaleX(1); }}
                48% {{ transform: scaleX(1); }}
                52% {{ transform: scaleX(-1); }}
                100% {{ left: 110%; transform: scaleX(-1); }}
            }}
            .container {{
                background: rgba(0, 60, 100, 0.9);
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 0 40px rgba(0, 200, 255, 0.1);
                padding: 40px;
                max-width: 500px;
                width: 100%;
                text-align: center;
                position: relative;
                z-index: 10;
                border: 2px solid rgba(0, 200, 255, 0.3);
            }}
            .status-icon {{
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, #00cc88 0%, #008855 100%);
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto 20px;
                animation: pulse 2s infinite;
                border: 3px solid rgba(0, 204, 136, 0.5);
            }}
            @keyframes pulse {{
                0%, 100% {{
                    transform: scale(1);
                    box-shadow: 0 0 20px rgba(0, 204, 136, 0.5);
                }}
                50% {{
                    transform: scale(1.05);
                    box-shadow: 0 0 40px rgba(0, 204, 136, 0.8);
                }}
            }}
            .shark-icon {{
                font-size: 50px;
            }}
            h1 {{
                color: #e0f7ff;
                margin-bottom: 10px;
                font-size: 28px;
                text-shadow: 0 0 10px rgba(0, 200, 255, 0.5);
            }}
            .status {{
                color: #00ff88;
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 30px;
                text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
            }}
            .info-grid {{
                display: grid;
                gap: 15px;
                margin-top: 30px;
            }}
            .info-item {{
                background: rgba(0, 100, 150, 0.3);
                padding: 15px;
                border-radius: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border: 1px solid rgba(0, 200, 255, 0.2);
            }}
            .info-label {{
                color: #7eb8d6;
                font-weight: 500;
            }}
            .info-value {{
                color: #e0f7ff;
                font-weight: bold;
            }}
            .bot-name {{
                color: #00ddff;
                font-weight: bold;
                text-shadow: 0 0 5px rgba(0, 221, 255, 0.5);
            }}
            .github-button {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 24px;
                background: rgba(36, 41, 47, 0.9);
                color: #ffffff;
                text-decoration: none;
                border-radius: 8px;
                border: 2px solid rgba(100, 180, 220, 0.3);
                transition: all 0.3s ease;
                font-weight: 500;
            }}
            .github-button:hover {{
                background: rgba(48, 54, 61, 1);
                border-color: rgba(100, 180, 220, 0.6);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }}
            @media (max-width: 480px) {{
                .container {{
                    padding: 30px 20px;
                }}
                h1 {{
                    font-size: 24px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="fish">🐠</div>
        <div class="fish">🐟</div>
        <div class="fish">🐡</div>
        <div class="container">
            <div class="status-icon">
                <span class="shark-icon">🦈</span>
            </div>
            <h1>Shark is <span class="status">Hunting</span></h1>
            <p style="color: #7eb8d6; margin-bottom: 20px;">All systems operational - cruising the deep</p>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">🦈 Shark Name</span>
                    <span class="info-value bot-name">{bot.user.name if bot.user else "Loading..."}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">⏱️ Swim Time</span>
                    <span class="info-value">{hours}h {minutes}m {seconds}s</span>
                </div>
                <div class="info-item">
                    <span class="info-label">🏝️ Ocean Territories</span>
                    <span class="info-value">{len(bot.guilds)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">📡 Sonar Ping</span>
                    <span class="info-value">{round(bot.latency * 1000)}ms</span>
                </div>
            </div>
            <a href="https://github.com/soryntech/discord-moderation-bot" target="_blank" class="github-button">
                🔗 View on GitHub
            </a>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(PORT))
    await site.start()
    print(f'Web server started on port {PORT}')


@bot.event
async def on_ready():
    global bot_start_time
    bot_start_time = datetime.datetime.now()
    print(f'{bot.user} has connected to Discord!')
    bot.loop.create_task(start_web_server())

    try:
        print("Attempting to sync commands...")
        synced = await bot.tree.sync()
        print(f"✅ Successfully synced {len(synced)} command(s)")
    except discord.Forbidden as e:
        print(f"❌ Failed to sync commands (insufficient permissions): {e}")
    except discord.HTTPException as e:
        print(f"❌ Failed to sync commands (HTTP error): {e}")
        print(f"Status: {e.status}")
        print(f"Response: {e.text}")
    except Exception as e:
        print(f"❌ Failed to sync commands (unexpected error): {e}")
        import traceback
        traceback.print_exc()


# Command check to block commands during emergency shutdown
async def check_emergency_shutdown(interaction: discord.Interaction) -> bool:
    global bot_emergency_shutdown

    # Allow owner commands regardless of shutdown status
    if interaction.user.id == 447812883158532106:
        return True

    # Block all commands during emergency shutdown (but NOT during owner sleep)
    if bot_emergency_shutdown:
        await interaction.response.send_message(
            "🔴 **Bot is currently offline due to emergency shutdown.**",
            ephemeral=True
        )
        return False

    # Owner sleep mode does NOT block commands - only changes status page
    return True


# Add event handler for rate limits
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        print(f"⏰ Command on cooldown: {error}")


@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(
    member="The member to kick",
    reason="Reason for kicking"
)
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    if not interaction.guild.me.guild_permissions.kick_members:
        await interaction.followup.send("❌ I don't have permission to kick members!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot kick this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    await member.kick(reason=reason)
    await interaction.followup.send(
        f"✅ {member.mention} has been kicked. Reason: {reason or 'No reason provided'}"
    )


@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(
    member="The member to ban",
    reason="Reason for banning"
)
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.followup.send("❌ I don't have permission to ban members!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot ban this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    await member.ban(reason=reason)
    await interaction.followup.send(
        f"✅ {member.mention} has been banned. Reason: {reason or 'No reason provided'}"
    )


@bot.tree.command(name="unban", description="Unban a user from the server")
@app_commands.describe(
    user_id="The user ID to unban"
)
@app_commands.checks.has_permissions(ban_members=True)
async def slash_unban(interaction: discord.Interaction, user_id: str):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.followup.send("❌ I don't have permission to unban members!", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.followup.send(f"✅ {user.mention} has been unbanned.")
    except discord.NotFound:
        await interaction.followup.send("❌ User not found or not banned.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to unban this user!", ephemeral=True)
    except ValueError:
        await interaction.followup.send("❌ Invalid user ID!", ephemeral=True)


@bot.tree.command(name="mute", description="Timeout a member")
@app_commands.describe(
    member="The member to mute",
    duration="Duration in seconds (default 60)",
    reason="Reason for muting"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_mute(interaction: discord.Interaction, member: discord.Member, duration: int = 60, reason: str = None):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.followup.send("❌ I don't have permission to timeout members!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot mute this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    duration_td = datetime.timedelta(seconds=duration)
    await member.timeout(duration_td, reason=reason)
    await interaction.followup.send(
        f"✅ {member.mention} has been muted for {duration} seconds. Reason: {reason or 'No reason provided'}"
    )


@bot.tree.command(name="unmute", description="Unmute a member")
@app_commands.describe(member="The member to unmute")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_unmute(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.followup.send("❌ I don't have permission!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot unmute this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    # Check if member is currently muted
    if member.timed_out_until is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not currently muted!",
            ephemeral=True
        )
        return

    # Unmute the member by removing the timeout
    try:
        await member.timeout(None, reason=f"Unmuted by {interaction.user}")
        await interaction.followup.send(
            f"✅ Successfully unmuted {member.mention}!"
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I don't have permission to unmute this member!",
            ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"❌ An error occurred: {e}",
            ephemeral=True
        )


@bot.tree.command(name="dc", description="Disconnect a user from voice")
@app_commands.describe(member="Member to disconnect")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_disconnect(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    # Check if bot has permission
    if not interaction.guild.me.guild_permissions.move_members:
        await interaction.response.send_message("❌ I don't have permission to move members!", ephemeral=True)
        return

    # Check if member is in a voice channel
    if member.voice is None or member.voice.channel is None:
        await interaction.response.send_message(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    # Check role hierarchy
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            "❌ I cannot disconnect this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    # Disconnect the member
    try:
        await interaction.response.defer()  # Only defer right before the action
        await member.move_to(None, reason=f"Disconnected by {interaction.user}")
        await interaction.followup.send(
            f"✅ Successfully disconnected {member.mention}!"
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I don't have permission to disconnect this member!",
            ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"❌ An error occurred: {e}",
            ephemeral=True
        )


@bot.tree.command(name="userpicture", description="Get a User's Profile Picture")
@app_commands.describe(member="The member to get picture of")
@app_commands.checks.has_permissions(send_messages=True)
@app_commands.checks.has_permissions(embed_links=True)
async def slash_userpicture(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    picture = member.display_avatar.url
    await interaction.followup.send(picture)


@bot.tree.command(name="userbanner", description="Get a user's nitro banner")
@app_commands.describe(member="The member to get nitro banner of")
@app_commands.checks.has_permissions(send_messages=True)
@app_commands.checks.has_permissions(embed_links=True)
async def slash_userbanner(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    user = await bot.fetch_user(member.id)

    if user.banner:
        banner = user.banner.url
        await interaction.followup.send(banner)
    else:
        await interaction.followup.send(f"{member.mention} does not have a banner.")


@bot.tree.command(name="userinfo", description="Get information about a user")
@app_commands.describe(member="The member to get info about (leave empty for yourself)")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    member = member or interaction.user

    embed = discord.Embed(
        title=f"User Info - {member}",
        color=member.color
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    # Basic user information
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)

    # Current status
    status_info = []
    if member.timed_out_until:
        status_info.append(f"⏱️ Timed out until: {member.timed_out_until.strftime('%Y-%m-%d %H:%M UTC')}")
    if member.voice:
        if member.voice.mute:
            status_info.append("🔇 Server Muted")
        if member.voice.deaf:
            status_info.append("🔈 Server Deafened")

    if status_info:
        embed.add_field(name="Current Status", value="\n".join(status_info), inline=False)

    # Roles
    roles = [role.mention for role in member.roles[1:]]
    if roles:
        embed.add_field(name="Roles", value=", ".join(roles), inline=False)

    # Moderation history
    mod_history = []
    try:
        # Check if bot has permission to view audit logs
        if not interaction.guild.me.guild_permissions.view_audit_log:
            embed.add_field(name="📋 Moderation History", value="⚠️ Bot lacks permission to view audit logs",
                            inline=False)
        else:
            # Fetch audit logs without any target filter
            entries_checked = 0
            async for entry in interaction.guild.audit_logs(limit=200):
                # Check if this entry targets our member
                if not entry.target:
                    continue

                # Compare IDs to filter for our specific member
                target_id = None
                if hasattr(entry.target, 'id'):
                    target_id = entry.target.id
                elif isinstance(entry.target, int):
                    target_id = entry.target

                if target_id != member.id:
                    continue

                entries_checked += 1

                # Process different action types
                if entry.action == discord.AuditLogAction.kick:
                    timestamp = entry.created_at.strftime("%Y-%m-%d %H:%M")
                    moderator = entry.user.mention if entry.user else "Unknown"
                    reason = entry.reason or "No reason provided"
                    mod_history.append(f"👢 **Kick** - {timestamp}\nBy: {moderator}\nReason: {reason}")

                elif entry.action == discord.AuditLogAction.ban:
                    timestamp = entry.created_at.strftime("%Y-%m-%d %H:%M")
                    moderator = entry.user.mention if entry.user else "Unknown"
                    reason = entry.reason or "No reason provided"
                    mod_history.append(f"🔨 **Ban** - {timestamp}\nBy: {moderator}\nReason: {reason}")

                elif entry.action == discord.AuditLogAction.unban:
                    timestamp = entry.created_at.strftime("%Y-%m-%d %H:%M")
                    moderator = entry.user.mention if entry.user else "Unknown"
                    reason = entry.reason or "No reason provided"
                    mod_history.append(f"✅ **Unban** - {timestamp}\nBy: {moderator}\nReason: {reason}")

                elif entry.action == discord.AuditLogAction.member_update:
                    # Check for timeout changes
                    try:
                        before_timeout = getattr(entry.before, 'timed_out_until', None)
                        after_timeout = getattr(entry.after, 'timed_out_until', None)

                        if before_timeout != after_timeout and after_timeout is not None:
                            timestamp = entry.created_at.strftime("%Y-%m-%d %H:%M")
                            moderator = entry.user.mention if entry.user else "Unknown"
                            reason = entry.reason or "No reason provided"
                            mod_history.append(f"⏱️ **Timeout** - {timestamp}\nBy: {moderator}\nReason: {reason}")
                    except AttributeError:
                        pass  # Skip if attributes don't exist

            if mod_history:
                # Limit to last 5 actions to avoid embed size limits
                history_text = "\n\n".join(mod_history[:5])
                if len(mod_history) > 5:
                    history_text += f"\n\n*...and {len(mod_history) - 5} more action(s)*"
                embed.add_field(name="📋 Moderation History", value=history_text, inline=False)
            else:
                embed.add_field(name="📋 Moderation History", value="No moderation actions found", inline=False)

    except discord.Forbidden:
        embed.add_field(name="📋 Moderation History", value="⚠️ Cannot access audit logs (Missing Permissions)",
                        inline=False)
    except Exception as e:
        embed.add_field(name="📋 Moderation History", value=f"⚠️ Error: {type(e).__name__}", inline=False)
        print(f"Audit log error: {type(e).__name__}: {str(e)}")  # Log to console for debugging

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="sdeaf", description="Deafen a user")
@app_commands.describe(member="The member to deafen")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_deaf(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    # Check if bot has permission
    if not interaction.guild.me.guild_permissions.deafen_members:
        await interaction.followup.send("❌ I don't have permission to deafen members!", ephemeral=True)
        return

    # Check if member is in a voice channel
    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    # Check if member is already deafened
    if member.voice.deaf:
        await interaction.followup.send(
            f"❌ {member.mention} is already server deafened!",
            ephemeral=True
        )
        return

    # Check role hierarchy
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot deafen this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    # Deafen the member
    try:
        await member.edit(deafen=True, reason=f"Server deafened by {interaction.user}")
        await interaction.followup.send(
            f"✅ Successfully server deafened {member.mention}!"
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I don't have permission to deafen this member!",
            ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"❌ An error occurred: {e}",
            ephemeral=True
        )


@bot.tree.command(name="smute", description="Mute a user")
@app_commands.describe(member="The member to mute")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_servermute(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    if not interaction.guild.me.guild_permissions.mute_members:
        await interaction.followup.send("I dont have permissions :angry_face:")
        return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send("Member role is too high or my role is too low")
        return
    # Check if member is in a voice channel
    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    # Check if member is already muted
    if member.voice.mute:
        await interaction.followup.send(
            f"❌ {member.mention} is already server muted!",
            ephemeral=True
        )
        return
    try:
        await member.edit(mute=True, reason=f"Server muted by {interaction.user}")
        await interaction.followup.send(
            f"✅ Successfully server Muted {member.mention}!"
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I don't have permission to Mute this member!",
            ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"❌ An error occurred: {e}",
            ephemeral=True
        )


@bot.tree.command(name="smuteno", description="Unmute a user from voice")
@app_commands.describe(member="The member to unmute")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_unmute_voice(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    # Check if bot has permission
    if not interaction.guild.me.guild_permissions.mute_members:
        await interaction.followup.send("❌ I don't have permission to mute/unmute members!", ephemeral=True)
        return

    # Check if member is in a voice channel
    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    # Check if member is actually muted
    if not member.voice.mute:
        await interaction.followup.send(
            f"❌ {member.mention} is not server muted!",
            ephemeral=True
        )
        return

    # Check role hierarchy
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot unmute this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    # Unmute the member
    try:
        await member.edit(mute=False, reason=f"Server unmuted by {interaction.user}")
        await interaction.followup.send(
            f"✅ Successfully server unmuted {member.mention}!"
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I don't have permission to unmute this member!",
            ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"❌ An error occurred: {e}",
            ephemeral=True
        )


@bot.tree.command(name="sdeafno", description="Undeafen a user from voice")
@app_commands.describe(member="The member to undeafen")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_undeaf_voice(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    # Check if bot has permission
    if not interaction.guild.me.guild_permissions.deafen_members:
        await interaction.followup.send("❌ I don't have permission to deafen/undeafen members!", ephemeral=True)
        return

    # Check if member is in a voice channel
    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    # Check if member is actually deafened
    if not member.voice.deaf:
        await interaction.followup.send(
            f"❌ {member.mention} is not server deafened!",
            ephemeral=True
        )
        return

    # Check role hierarchy
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot undeafen this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    # Undeafen the member
    try:
        await member.edit(deafen=False, reason=f"Server undeafened by {interaction.user}")
        await interaction.followup.send(
            f"✅ Successfully server undeafened {member.mention}!"
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I don't have permission to undeafen this member!",
            ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"❌ An error occurred: {e}",
            ephemeral=True
        )


@bot.tree.command(name="purge", description="Mass Delete Messages")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(msgamount="How many Messages you want to delete")
async def slash_purge_messages(interaction: discord.Interaction, msgamount: int):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    if not interaction.guild.me.guild_permissions.manage_messages:
        await interaction.followup.send("I do not have Permissions!", ephemeral=True)
        return
    if msgamount <= 0:
        await interaction.followup.send("The message amount needs to be greater than 0!", ephemeral=True)
        return
    if msgamount > 100:
        await interaction.followup.send("You cannot do over 100 messages at a time", ephemeral=True)
        return
    try:
        deleted = await interaction.channel.purge(limit=msgamount)
        await interaction.followup.send(f"Successfully deleted {len(deleted)} messages!", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to delete messages in this channel!", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"An error occurred while deleting messages: {e}", ephemeral=True)


@bot.tree.command(name="lockdown", description="Lock down the server")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(message="(Optional) Lockdown Message")
async def slash_lockdown(interaction: discord.Interaction, message: str = None):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    if not interaction.guild.me.guild_permissions.manage_channels:
        await interaction.followup.send("I do not have Permissions to manage channels!", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.administrator:
        await interaction.followup.send("I do not have administrator permissions!", ephemeral=True)
        return

    try:
        locked_count = 0
        failed_channels = []

        # Loop through all text channels
        for channel in interaction.guild.text_channels:
            try:
                # Deny send messages for @everyone role
                await channel.set_permissions(
                    interaction.guild.default_role,
                    send_messages=False,
                    reason=f"Server lockdown by {interaction.user}"
                )
                locked_count += 1
            except discord.Forbidden:
                failed_channels.append(channel.name)
            except discord.HTTPException:
                failed_channels.append(channel.name)

        # Send response
        response = f"🔒 **Server Locked Down**\n✅ Locked {locked_count} channels"
        if failed_channels:
            response += f"\n❌ Failed to lock: {', '.join(failed_channels)}"
        if message:
            response += f"\n\n📢 **Message:** {message}"

        await interaction.followup.send(response)

    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred during lockdown: {e}", ephemeral=True)


@bot.tree.command(name="killswitch", description="Emergency bot shutdown (Owner Only)")
async def slash_killswitch(interaction: discord.Interaction):
    global bot_emergency_shutdown

    # Check if user is the bot owner
    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    # Toggle emergency shutdown mode
    bot_emergency_shutdown = not bot_emergency_shutdown

    if bot_emergency_shutdown:
        # Set bot status to invisible
        await bot.change_presence(status=discord.Status.invisible)
        await interaction.response.send_message(
            "🔴 **EMERGENCY SHUTDOWN ACTIVATED**\n"
            "All commands are now disabled except /restart-bot.\n"
            "The status page now shows the bot as offline.\n"
            "Bot status set to invisible.",
            ephemeral=True
        )
    else:
        # Set bot status back to online
        await bot.change_presence(status=discord.Status.online)
        await interaction.response.send_message(
            "✅ **EMERGENCY SHUTDOWN DEACTIVATED**\n"
            "Bot is now accepting commands normally.\n"
            "Bot status set to online.",
            ephemeral=True
        )


@bot.tree.command(name="restart-bot", description="Restart the bot from emergency shutdown (Owner Only)")
async def slash_restart_bot(interaction: discord.Interaction):
    global bot_emergency_shutdown

    # Check if user is the bot owner
    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    if not bot_emergency_shutdown:
        await interaction.response.send_message(
            "ℹ️ Bot is not in emergency shutdown mode.",
            ephemeral=True
        )
        return

    bot_emergency_shutdown = False
    # Set bot status back to online
    await bot.change_presence(status=discord.Status.online)
    await interaction.response.send_message(
        "✅ **BOT RESTARTED**\n"
        "Emergency shutdown mode disabled. Bot is now accepting all commands.\n"
        "Bot status set to online.",
        ephemeral=True
    )


@bot.tree.command(name="owner-sleep", description="Toggle owner sleep status page (Owner Only)")
async def slash_owner_sleep(interaction: discord.Interaction):
    global bot_owner_sleeping

    # Check if user is the bot owner
    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    # Toggle owner sleep mode
    bot_owner_sleeping = not bot_owner_sleeping

    if bot_owner_sleeping:
        await interaction.response.send_message(
            "😴 **OWNER SLEEP STATUS ENABLED**\n"
            "The status page now shows 'Shark Owner is Sleeping' with the message about GitHub PRs.\n"
            "⚠️ Note: Bot commands remain fully functional.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "✅ **OWNER SLEEP STATUS DISABLED**\n"
            "The status page now shows normal bot status.",
            ephemeral=True
        )


@bot.tree.command(name="updatemode", description="Toggle update mode for the bot status page (Owner Only)")
async def slash_updatemode(interaction: discord.Interaction):
    global bot_updating

    # Check if user is the bot owner
    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    # Toggle update mode
    bot_updating = not bot_updating

    if bot_updating:
        # Set bot status to idle
        await bot.change_presence(status=discord.Status.idle)
        await interaction.response.send_message(
            "🔄 **UPDATE MODE ENABLED**\n"
            "The status page now displays 'Shark Bot is Updating'.\n"
            "Bot status set to idle.\n"
            "Use this command again to disable update mode.",
            ephemeral=True
        )
    else:
        # Set bot status back to online
        await bot.change_presence(status=discord.Status.online)
        await interaction.response.send_message(
            "✅ **UPDATE MODE DISABLED**\n"
            "The status page now shows normal bot status.\n"
            "Bot status set to online.",
            ephemeral=True
        )


@bot.tree.command(name="ping", description="Check the bot's latency")
async def slash_ping(interaction: discord.Interaction):
    if not await check_emergency_shutdown(interaction):
        return

    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot Latency: **{latency}ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unlockserver", description="Unlock the server")
@app_commands.checks.has_permissions(administrator=True)
async def slash_unlockserver(interaction: discord.Interaction):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    if not interaction.guild.me.guild_permissions.manage_channels:
        await interaction.followup.send("I do not have Permissions to manage channels!", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.administrator:
        await interaction.followup.send("I do not have administrator permissions!", ephemeral=True)
        return

    try:
        unlocked_count = 0
        failed_channels = []

        # Loop through all text channels
        for channel in interaction.guild.text_channels:
            try:
                # Re-enable send messages for @everyone role
                await channel.set_permissions(
                    interaction.guild.default_role,
                    send_messages=None,  # None resets to default/removes override
                    reason=f"Server unlocked by {interaction.user}"
                )
                unlocked_count += 1
            except discord.Forbidden:
                failed_channels.append(channel.name)
            except discord.HTTPException:
                failed_channels.append(channel.name)

        # Send response
        response = f"🔓 **Server Unlocked**\n✅ Unlocked {unlocked_count} channels"
        if failed_channels:
            response += f"\n❌ Failed to unlock: {', '.join(failed_channels)}"

        await interaction.followup.send(response)

    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred during unlock: {e}", ephemeral=True)


@bot.tree.command(name="nickname", description="Change a users nickname")
@app_commands.checks.has_permissions(manage_nicknames=True)
@app_commands.describe(
    member="The member to change nickname",
    nickname="New nickname (leave empty to reset)"
)
@app_commands.checks.has_permissions(manage_nicknames=True)
async def slash_nickname(interaction: discord.Interaction, member: discord.Member, nickname: str = None):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    if not interaction.guild.me.guild_permissions.manage_nicknames:
        await interaction.followup.send("❌ I don't have permission to manage nicknames!", ephemeral=True)
        return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot change this member's nickname (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return
    try:
        old_nick = member.nick or member.name
        await member.edit(nick=nickname, reason=f"Nickname changed by {interaction.user}")

        if nickname:
            await interaction.followup.send(
                f"✅ Changed {member.mention}'s nickname from **{old_nick}** to **{nickname}**")
        else:
            await interaction.followup.send(f"✅ Reset {member.mention}'s nickname (was **{old_nick}**)")

    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to change this member's nickname!", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)


@bot.tree.command(name="serverinfo", description="Display server information")
async def slash_serverinfo(interaction: discord.Interaction):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    guild = interaction.guild

    # Count members by status
    online = sum(1 for m in guild.members if m.status == discord.Status.online)
    idle = sum(1 for m in guild.members if m.status == discord.Status.idle)
    dnd = sum(1 for m in guild.members if m.status == discord.Status.dnd)
    offline = sum(1 for m in guild.members if m.status == discord.Status.offline)

    # Count bots
    bots = sum(1 for m in guild.members if m.bot)
    humans = len(guild.members) - bots

    embed = discord.Embed(
        title=f"📊 {guild.name} Server Information",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    # Basic Info
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)

    # Member Stats
    embed.add_field(
        name=f"Members ({len(guild.members)})",
        value=f"👤 Humans: {humans}\n🤖 Bots: {bots}",
        inline=True
    )

    embed.add_field(
        name="Member Status",
        value=f"🟢 | Online | {online}\n🟡 | Idle | {idle}\n🔴 | DND | {dnd}\n⚫ | Offline | {offline}",
        inline=True
    )

    # Channel Stats
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)

    embed.add_field(
        name="Channels",
        value=f"💬 Text: {text_channels}\n🔊 Voice: {voice_channels}\n📁 Categories: {categories}",
        inline=True
    )

    # Role and Emoji Info
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
    embed.add_field(name="Boosts", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)",
                    inline=True)

    # Verification Level
    embed.add_field(name="Verification Level", value=str(guild.verification_level).title(), inline=True)

    # Server Features
    if guild.features:
        features = ", ".join([f.replace("_", " ").title() for f in guild.features[:5]])
        if len(guild.features) > 5:
            features += f" (+{len(guild.features) - 5} more)"
        embed.add_field(name="Features", value=features, inline=False)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="modnote", description="Add a note about a user (visible only to mods)")
@app_commands.describe(
    user="The user to add a note about",
    note="The note content"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_modnote(interaction: discord.Interaction, user: discord.User, note: str):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    # Store the note in your database here
    # Example: await db.add_modnote(interaction.guild.id, user.id, interaction.user.id, note)

    await interaction.followup.send(
        f"✅ Moderation note added for {user.mention}:\n```{note}```",
        ephemeral=True
    )


@bot.tree.command(name="warn", description="Issue a warning to a user")
@app_commands.describe(
    member="The member to warn",
    reason="Reason for the warning"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()

    # Store the warning in your database here
    # Example: case_id = await db.add_warning(interaction.guild.id, member.id, interaction.user.id, reason)

    try:
        await member.send(
            f"⚠️ You have been warned in **{interaction.guild.name}**\n"
            f"**Reason:** {reason}\n"
            f"**Moderator:** {interaction.user.mention}"
        )
        dm_status = "User has been notified via DM."
    except discord.Forbidden:
        dm_status = "Could not DM the user."

    await interaction.followup.send(
        f"✅ {member.mention} has been warned.\n"
        f"**Reason:** {reason}\n"
        f"{dm_status}"
    )


@bot.tree.command(name="warnings", description="View warnings for a specific user")
@app_commands.describe(
    user="The user to view warnings for"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_warnings(interaction: discord.Interaction, user: discord.User):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    # Fetch warnings from your database here
    # Example: warnings = await db.get_warnings(interaction.guild.id, user.id)

    # Mock data for demonstration
    warnings = []  # Replace with actual database query

    if not warnings:
        await interaction.followup.send(
            f"ℹ️ {user.mention} has no warnings.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"Warnings for {user.name}",
        description=f"Total warnings: {len(warnings)}",
        color=discord.Color.orange()
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    for idx, warning in enumerate(warnings[:10], 1):  # Show last 10 warnings
        # Example warning structure: {case_id, reason, moderator_id, timestamp}
        embed.add_field(
            name=f"Case #{warning['case_id']} - {warning['timestamp']}",
            value=f"**Reason:** {warning['reason']}\n**Moderator:** <@{warning['moderator_id']}>",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="clearwarns", description="Clear all warnings for a user")
@app_commands.describe(
    user="The user to clear warnings for"
)
@app_commands.checks.has_permissions(administrator=True)
async def slash_clearwarns(interaction: discord.Interaction, user: discord.User):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    # Clear warnings from your database here
    # Example: count = await db.clear_warnings(interaction.guild.id, user.id)

    count = 0  # Replace with actual count from database

    if count == 0:
        await interaction.followup.send(
            f"ℹ️ {user.mention} has no warnings to clear.",
            ephemeral=True
        )
        return

    await interaction.followup.send(
        f"✅ Cleared {count} warning(s) for {user.mention}",
        ephemeral=True
    )


@bot.tree.command(name="case", description="View details of a specific moderation case")
@app_commands.describe(
    case_id="The case ID to view"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_case(interaction: discord.Interaction, case_id: int):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    # Fetch case from your database here
    # Example: case = await db.get_case(interaction.guild.id, case_id)

    case = None  # Replace with actual database query

    if not case:
        await interaction.followup.send(
            f"❌ Case #{case_id} not found.",
            ephemeral=True
        )
        return

    # Example case structure: {case_id, type, user_id, moderator_id, reason, timestamp}
    embed = discord.Embed(
        title=f"Case #{case['case_id']}",
        color=discord.Color.blue(),
        timestamp=case['timestamp']
    )
    embed.add_field(name="Type", value=case['type'].capitalize(), inline=True)
    embed.add_field(name="User", value=f"<@{case['user_id']}>", inline=True)
    embed.add_field(name="Moderator", value=f"<@{case['moderator_id']}>", inline=True)
    embed.add_field(name="Reason", value=case['reason'] or "No reason provided", inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="reason", description="Add/edit reason for a moderation action")
@app_commands.describe(
    case_id="The case ID to update",
    reason="The new reason"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_reason(interaction: discord.Interaction, case_id: int, reason: str):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    # Update reason in your database here
    # Example: success = await db.update_case_reason(interaction.guild.id, case_id, reason)

    success = True  # Replace with actual database operation

    if not success:
        await interaction.followup.send(
            f"❌ Case #{case_id} not found or could not be updated.",
            ephemeral=True
        )
        return

    await interaction.followup.send(
        f"✅ Updated reason for case #{case_id}:\n```{reason}```",
        ephemeral=True
    )

#=====================================================WIP (INFO)=====================================================

#@bot.tree.command(name="member-count",description="Display server member statistics")
#async def slash_member_count(interaction: discord.Interaction):
    #print("save indent")
#@bot.tree.command(name="bot-info", description="Display bot statistics and information")
#async def slash_bot_info(interaction: discord.Interaction):
    #print("Save indent")
# ===============WIP ROLE MANAGMENT================================================================================
@bot.tree.command(name="addrole", description="Add a role to a user")
async def slash_addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not await check_emergency_shutdown(interaction):
        return

    # Check if the bot has permission to manage roles
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message("I don't have permission to manage roles!", ephemeral=True)
        return

    # Check if the command user has permission to manage roles
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to manage roles!", ephemeral=True)
        return

    # Check if the bot's highest role is higher than the role to add
    if interaction.guild.me.top_role <= role:
        await interaction.response.send_message(
            f"I cannot add {role.mention} because it's higher than or equal to my highest role!", ephemeral=True)
        return

    # Check if the user's highest role is higher than the role to add
    if interaction.user.top_role <= role and interaction.user != interaction.guild.owner:
        await interaction.response.send_message(
            f"You cannot add {role.mention} because it's higher than or equal to your highest role!", ephemeral=True)
        return

    # Check if the member already has the role
    if role in member.roles:
        await interaction.response.send_message(f"{member.mention} already has the {role.mention} role!",
                                                ephemeral=True)
        return

    # Add the role
    try:
        await member.add_roles(role, reason=f"Role added by {interaction.user}")
        await interaction.response.send_message(f"Successfully added {role.mention} to {member.mention}!")
    except discord.Forbidden:
        await interaction.response.send_message("Failed to add role due to permission issues!", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


@bot.tree.command(name="role-count", description="Show how many users have a role")
async def slash_rolecount(interaction: discord.Interaction, role: discord.Role):
    if not await check_emergency_shutdown(interaction):
        return

    # Count members who have this role
    member_count = len(role.members)

    # Create an embed
    embed = discord.Embed(
        title="📊 Role Statistics",
        color=role.color
    )

    embed.add_field(name="Role", value=role.mention, inline=True)
    embed.add_field(name="Member Count", value=f"**{member_count}**", inline=True)
    embed.add_field(name="Role ID", value=f"`{role.id}`", inline=False)

    # Add a footer with timestamp
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    embed.timestamp = interaction.created_at

    await interaction.response.send_message(embed=embed)


# error handling
@slash_ban.error
@slash_kick.error
@slash_mute.error
@slash_servermute.error
@slash_unban.error
@slash_userpicture.error
@slash_userbanner.error
@slash_userinfo.error
@slash_disconnect.error
@slash_deaf.error
@slash_unmute_voice.error
@slash_undeaf_voice.error
@slash_purge_messages.error
@slash_lockdown.error
@slash_unlockserver.error
@slash_nickname.error
@slash_serverinfo.error
@slash_ping.error
@slash_addrole.error
@slash_rolecount.error
@slash_unmute.error
async def permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        try:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command!",
                ephemeral=True
            )
        except:
            await interaction.followup.send(
                "❌ You don't have permission to use this command!",
                ephemeral=True
            )
    elif isinstance(error, app_commands.BotMissingPermissions):
        try:
            await interaction.response.send_message(
                "❌ I don't have the required permissions to execute this command!",
                ephemeral=True
            )
        except:
            await interaction.followup.send(
                "❌ I don't have the required permissions to execute this command!",
                ephemeral=True
            )
    elif isinstance(error, app_commands.CommandOnCooldown):
        try:
            await interaction.response.send_message(
                f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        except:
            await interaction.followup.send(
                f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
    else:
        # Log unexpected errors
        print(f"Unexpected error in command: {error}")
        try:
            await interaction.response.send_message(
                "❌ An unexpected error occurred while executing this command.",
                ephemeral=True
            )
        except:
            try:
                await interaction.followup.send(
                    "❌ An unexpected error occurred while executing this command.",
                    ephemeral=True
                )
            except:
                pass


@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def prefix_kick(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.kick_members:
        await ctx.send("❌ I don't have permission to kick members!")
        return
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ I cannot kick this member (their role is equal or higher than mine)!")
        return
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} has been kicked. Reason: {reason or 'No reason provided'}")


@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def prefix_ban(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("❌ I don't have permission to ban members!")
        return
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ I cannot ban this member (their role is equal or higher than mine)!")
        return
    await member.ban(reason=reason)
    await ctx.send(f"✅ {member.mention} has been banned. Reason: {reason or 'No reason provided'}")


if __name__ == "__main__":
    print("=== BOT STARTING ===")
    print(f"TOKEN exists: {bool(TOKEN)}")
    print(f"PORT: {PORT}")

    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found in environment variables!")
        print("Make sure your .env file contains DISCORD_TOKEN=your_token_here")
    else:
        print("Starting bot...")
        try:
            bot.run(TOKEN, log_handler=None)  # Use our custom logging
        except Exception as e:
            print(f"BOT CRASHED: {e}")
            import traceback
            import traceback

            traceback.print_exc()

    print("=== BOT EXITED ===")
