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
# End Initalization


# Set up logging to see rate limit info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

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
    global bot_updating

    if bot_start_time is None:
        return web.Response(
            text="Bot is starting up, please wait...",
            content_type='text/plain',
            status=503
        )

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
                    background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }
                .container {
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    padding: 40px;
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                }
                .status-icon {
                    width: 80px;
                    height: 80px;
                    background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0 auto 20px;
                    animation: spin 2s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .update-icon {
                    font-size: 40px;
                    color: white;
                }
                h1 {
                    color: #333;
                    margin-bottom: 10px;
                    font-size: 28px;
                }
                .status {
                    color: #ff6b35;
                    font-weight: bold;
                    font-size: 18px;
                    margin-bottom: 30px;
                }
                .info-message {
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    border-radius: 5px;
                    color: #856404;
                    margin-top: 20px;
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
            <div class="container">
                <div class="status-icon">
                    <span class="update-icon">⟳</span>
                </div>
                <h1>Bot is <span class="status">Updating</span></h1>
                <p style="color: #666; margin-bottom: 20px;">Maintenance in progress</p>
                <div class="info-message">
                    ⚠️ The bot is currently being updated. Please check back in a few minutes.
                </div>
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 500px;
                width: 100%;
                text-align: center;
            }}
            .status-icon {{
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto 20px;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{
                    transform: scale(1);
                    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
                }}
                50% {{
                    transform: scale(1.05);
                    box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
                }}
            }}
            .checkmark {{
                font-size: 40px;
                color: white;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }}
            .status {{
                color: #4CAF50;
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 30px;
            }}
            .info-grid {{
                display: grid;
                gap: 15px;
                margin-top: 30px;
            }}
            .info-item {{
                background: #f5f5f5;
                padding: 15px;
                border-radius: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .info-label {{
                color: #666;
                font-weight: 500;
            }}
            .info-value {{
                color: #333;
                font-weight: bold;
            }}
            .bot-name {{
                color: #667eea;
                font-weight: bold;
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
        <div class="container">
            <div class="status-icon">
                <span class="checkmark">✓</span>
            </div>
            <h1>Bot is <span class="status">Online</span></h1>
            <p style="color: #666; margin-bottom: 20px;">All systems operational</p>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Bot Name</span>
                    <span class="info-value bot-name">{bot.user.name if bot.user else "Loading..."}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Uptime</span>
                    <span class="info-value">{hours}h {minutes}m {seconds}s</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Servers</span>
                    <span class="info-value">{len(bot.guilds)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Latency</span>
                    <span class="info-value">{round(bot.latency * 1000)}ms</span>
                </div>
            </div>
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
    await interaction.response.defer()
    picture = member.display_avatar.url
    await interaction.followup.send(picture)


@bot.tree.command(name="userbanner", description="Get a user's nitro banner")
@app_commands.describe(member="The member to get nitro banner of")
@app_commands.checks.has_permissions(send_messages=True)
@app_commands.checks.has_permissions(embed_links=True)
async def slash_userbanner(interaction: discord.Interaction, member: discord.Member):
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
    # Check if user is the bot owner
    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    await interaction.response.send_message("🔴 **EMERGENCY SHUTDOWN INITIATED**\nBot is shutting down...")

    # Close the bot
    await bot.close()


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
        await interaction.response.send_message(
            "🔄 **UPDATE MODE ENABLED**\n"
            "The status page now displays 'Bot is Updating'.\n"
            "Use this command again to disable update mode.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "✅ **UPDATE MODE DISABLED**\n"
            "The status page now shows normal bot status.",
            ephemeral=True
        )


@bot.tree.command(name="ping", description="Check the bot's latency")
async def slash_ping(interaction: discord.Interaction):
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



#===============WIP ROLE MANAGMENT================================================================================
@bot.tree.command(name="addrole", description="Add a role to a user")
async def slash_addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
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

            traceback.print_exc()

    print("=== BOT EXITED ===")
