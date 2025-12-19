import os
import discord
from discord import app_commands, Member
from discord.ext import commands
import datetime
import requests
import random as r
from aiohttp import web

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
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except discord.Forbidden as e:
        print(f"Failed to sync commands (insufficient permissions): {e}")
    except discord.HTTPException as e:
        print(f"Failed to sync commands (HTTP error): {e}")
    except Exception as e:
        print(f"Failed to sync commands (unexpected error): {e}")
        raise



@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(
    member="The member to kick",
    reason="Reason for kicking"
)
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.guild.me.guild_permissions.kick_members:
        await interaction.response.send_message("❌ I don't have permission to kick members!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            "❌ I cannot kick this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    await member.kick(reason=reason)
    await interaction.response.send_message(
        f"✅ {member.mention} has been kicked. Reason: {reason or 'No reason provided'}"
    )


@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(
    member="The member to ban",
    reason="Reason for banning"
)
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ I don't have permission to ban members!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            "❌ I cannot ban this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    await member.ban(reason=reason)
    await interaction.response.send_message(
        f"✅ {member.mention} has been banned. Reason: {reason or 'No reason provided'}"
    )


@bot.tree.command(name="unban", description="Unban a user from the server")
@app_commands.describe(
    user_id="The user ID to unban"
)
@app_commands.checks.has_permissions(ban_members=True)
async def slash_unban(interaction: discord.Interaction, user_id: str):
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ I don't have permission to unban members!", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ {user.mention} has been unbanned.")
    except discord.NotFound:
        await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to unban this user!", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("❌ Invalid user ID!", ephemeral=True)


@bot.tree.command(name="mute", description="Timeout a member")
@app_commands.describe(
    member="The member to mute",
    duration="Duration in seconds (default 60)",
    reason="Reason for muting"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_mute(interaction: discord.Interaction, member: discord.Member, duration: int = 60, reason: str = None):

    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ I don't have permission to timeout members!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            "❌ I cannot mute this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    duration_td = datetime.timedelta(seconds=duration)
    await member.timeout(duration_td, reason=reason)
    await interaction.response.send_message(
        f"✅ {member.mention} has been muted for {duration} seconds. Reason: {reason or 'No reason provided'}"
    )


@bot.tree.command(name="userpicture", description="Get a User's Profile Picture")
@app_commands.describe(member="The member to get picture of")
@app_commands.checks.has_permissions(send_messages=True)
@app_commands.checks.has_permissions(embed_links=True)
async def slash_userpicture(interaction: discord.Interaction, member: discord.Member):
    picture = member.display_avatar.url
    await interaction.response.send_message(picture)


@bot.tree.command(name="userbanner", description="Get a user's nitro banner")
@app_commands.describe(member="The member to get nitro banner of")
@app_commands.checks.has_permissions(send_messages=True)
@app_commands.checks.has_permissions(embed_links=True)
async def slash_userbanner(interaction: discord.Interaction, member: discord.Member):
    user = await bot.fetch_user(member.id)

    if user.banner:
        banner = user.banner.url
        await interaction.response.send_message(banner)
    else:
        await interaction.response.send_message(f"{member.mention} does not have a banner.")


@bot.tree.command(name="userinfo", description="Get information about a user")
@app_commands.describe(member="The member to get info about (leave empty for yourself)")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_userinfo(interaction: discord.Interaction, member: discord.Member = None):
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
        # Fetch audit logs for moderation actions
        async for entry in interaction.guild.audit_logs(limit=100, user=member):
            if entry.action in [
                discord.AuditLogAction.kick,
                discord.AuditLogAction.ban,
                discord.AuditLogAction.member_update,  # For timeouts, mutes, deafens
                discord.AuditLogAction.unban
            ]:
                action_name = entry.action.name.replace('_', ' ').title()
                timestamp = entry.created_at.strftime("%Y-%m-%d %H:%M")
                moderator = entry.user.mention if entry.user else "Unknown"
                reason = entry.reason or "No reason provided"

                # Filter for timeout/mute/deafen actions
                if entry.action == discord.AuditLogAction.member_update:
                    if entry.before.timed_out_until != entry.after.timed_out_until:
                        if entry.after.timed_out_until:
                            mod_history.append(f"⏱️ **Timeout** - {timestamp}\nBy: {moderator}\nReason: {reason}")
                    # Note: Voice mute/deafen changes are harder to track via audit logs
                else:
                    emoji = "👢" if entry.action == discord.AuditLogAction.kick else "🔨" if entry.action == discord.AuditLogAction.ban else "✅"
                    mod_history.append(f"{emoji} **{action_name}** - {timestamp}\nBy: {moderator}\nReason: {reason}")

        if mod_history:
            # Limit to last 5 actions to avoid embed size limits
            history_text = "\n\n".join(mod_history[:5])
            if len(mod_history) > 5:
                history_text += f"\n\n*...and {len(mod_history) - 5} more action(s)*"
            embed.add_field(name="📋 Moderation History", value=history_text, inline=False)
        else:
            embed.add_field(name="📋 Moderation History", value="No moderation actions found", inline=False)
    except discord.Forbidden:
        embed.add_field(name="📋 Moderation History", value="⚠️ Cannot access audit logs", inline=False)

    await interaction.response.send_message(embed=embed)


#error handling
@slash_ban.error
@slash_kick.error
@slash_mute.error
@slash_unban.error
@slash_userpicture.error
@slash_userbanner.error
@slash_userinfo.error
async def permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
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
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found in environment variables!")
        print("Make sure your .env file contains DISCORD_TOKEN=your_token_here")
    else:
        print("Starting bot...")
        bot.run(TOKEN)