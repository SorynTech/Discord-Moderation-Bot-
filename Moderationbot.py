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
    if bot_start_time is None:
        return web.Response(
            text="Bot is starting up, please wait...",
            content_type='text/plain',
            status=503
        )

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


# error handling
@slash_ban.error
@slash_kick.error
@slash_mute.error
@slash_unban.error
@slash_userpicture.error
@slash_userbanner.error
@slash_userinfo.error
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