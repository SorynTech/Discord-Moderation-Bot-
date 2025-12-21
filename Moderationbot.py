import os
import discord
from discord import app_commands, Member
from discord.ext import commands
import datetime
import requests
import random as r
from aiohttp import web
import logging

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
    return web.Response(text="Bot is running!")


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
@app_commands.describe(member="member to disconnect")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_disconnect(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer
    # Check if bot has permission
    if not interaction.guild.me.guild_permissions.move_members:
        await interaction.followup.send("❌ I don't have permission to move members!", ephemeral=True)
        return
    # Check if member is in a voice channel
    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        # Check role hierarchy
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.followup.send(
                "❌ I cannot disconnect this member (their role is equal or higher than mine)!",
                ephemeral=True
            )
        try:
            await member.move_to(None, reason=f"Disconnected by {interaction.user}")
            await interaction.followup.send("Succsesfully Disconnected Member :sleepy:", ephemeral=True)
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
@bot.tree.command(name="smute",description="Mute a user")
@app_commands.describe(member="The member to mute")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_mute(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    if not interaction.guild.me.guild_permissions.mute_members:
        await interaction.followup.send("I dont have permissions :angry_face:")
        return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send("Member role is too high or my role is too low")
        return
        # Check if member is already deafened
    if member.voice.mute:
        await interaction.followup.send(
            f"❌ {member.mention} is already server muted!",
            ephemeral=True
            )
        return
    try:
        await member.edit(mute=True, reason=f"Server muted by {interaction.user}")
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