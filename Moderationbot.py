import sys
import os
import base64

# Force unbuffered output - CRITICAL for seeing logs on Render
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

print("=" * 60, flush=True)
print("STEP 1: Script file loaded", flush=True)
print("=" * 60, flush=True)

print("STEP 2: Importing standard libraries...", flush=True)
from datetime import datetime, timedelta

print(f"  ✓ datetime imported at {datetime.now()}", flush=True)

print("STEP 3: Checking environment...", flush=True)
print(f"  Python: {sys.version.split()[0]}", flush=True)
print(f"  Directory: {os.getcwd()}", flush=True)
print(f"  DISCORD_TOKEN exists: {bool(os.getenv('DISCORD_TOKEN'))}", flush=True)

print("STEP 4: Importing discord.py (this may take 10-30 seconds)...", flush=True)
try:
    import discord

    print(f"  ✓ discord.py {discord.__version__} imported", flush=True)
except Exception as e:
    print(f"  ✗ FAILED to import discord.py: {e}", flush=True)
    sys.exit(1)

print("STEP 5: Importing other dependencies...", flush=True)

from discord import app_commands, Member
from discord.ext import commands
import requests
import random as r
from aiohttp import web
import logging
import asyncio

# Track bot start time for uptime
bot_start_time = None
if bot_start_time is None:
    bot_start_time = datetime.now()

# Track update status
bot_updating = False
# Track emergency shutdown status
bot_emergency_shutdown = False
# Track owner sleep status
bot_owner_sleeping = False
# Track if commands are synced to prevent multiple syncs
commands_synced = False
# ============================================================================
# DATABASE CONFIGURATION AND FUNCTIONS FOR MODERATION BOT
# ============================================================================
# PASTE THIS SECTION AFTER THE IMPORTS AND BEFORE THE INTENTS CONFIGURATION
# (Around line 50-60, after all the import statements)
# ============================================================================

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from typing import Optional, List, Dict

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================



# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================

def get_db_connection():
    """Get a database connection from the pool"""
    return db_pool.getconn()


def return_db_connection(conn):
    """Return a connection to the pool"""
    db_pool.putconn(conn)


def init_moderation_database():
    """Initialize database with moderation tracking tables"""
    global db_pool

    print("=" * 60)
    print("🗄️  INITIALIZING MODERATION DATABASE")
    print("=" * 60)

    if not SUPABASE_URL:
        print("❌ SUPABASE_URL not found in environment variables!")
        print("⚠️  Moderation tracking features will be disabled.")
        print("Add SUPABASE_URL to your .env file to enable moderation tracking.")
        return False

    try:
        # Create connection pool
        print("🔄 Creating database connection pool...")
        db_pool = SimpleConnectionPool(1, 20, SUPABASE_URL)
        print("✅ Database connection pool created")

        print("🔌 Testing database connection...")
        conn = get_db_connection()
        cur = conn.cursor()
        print("✅ Database connection successful")

        # Create moderation_cases table
        print("📋 Creating 'moderation_cases' table...")
        cur.execute('''CREATE TABLE IF NOT EXISTS moderation_cases
                       (
                           case_id
                           SERIAL
                           PRIMARY
                           KEY,
                           guild_id
                           BIGINT
                           NOT
                           NULL,
                           user_id
                           BIGINT
                           NOT
                           NULL,
                           moderator_id
                           BIGINT
                           NOT
                           NULL,
                           action_type
                           TEXT
                           NOT
                           NULL,
                           reason
                           TEXT,
                           user_name
                           TEXT,
                           moderator_name
                           TEXT,
                           created_at
                           TIMESTAMP
                           WITH
                           TIME
                           ZONE
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           WITH
                           TIME
                           ZONE
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )''')
        print("✅ 'moderation_cases' table ready (includes usernames)")

        # Create moderation_warnings table
        print("📋 Creating 'moderation_warnings' table...")
        cur.execute('''CREATE TABLE IF NOT EXISTS moderation_warnings
                       (
                           warning_id
                           SERIAL
                           PRIMARY
                           KEY,
                           guild_id
                           BIGINT
                           NOT
                           NULL,
                           user_id
                           BIGINT
                           NOT
                           NULL,
                           moderator_id
                           BIGINT
                           NOT
                           NULL,
                           reason
                           TEXT
                           NOT
                           NULL,
                           user_name
                           TEXT,
                           moderator_name
                           TEXT,
                           created_at
                           TIMESTAMP
                           WITH
                           TIME
                           ZONE
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )''')
        print("✅ 'moderation_warnings' table ready (includes usernames)")

        # Create moderation_notes table
        print("📋 Creating 'moderation_notes' table...")
        cur.execute('''CREATE TABLE IF NOT EXISTS moderation_notes
                       (
                           note_id
                           SERIAL
                           PRIMARY
                           KEY,
                           guild_id
                           BIGINT
                           NOT
                           NULL,
                           user_id
                           BIGINT
                           NOT
                           NULL,
                           moderator_id
                           BIGINT
                           NOT
                           NULL,
                           note_text
                           TEXT
                           NOT
                           NULL,
                           user_name
                           TEXT,
                           moderator_name
                           TEXT,
                           created_at
                           TIMESTAMP
                           WITH
                           TIME
                           ZONE
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )''')
        print("✅ 'moderation_notes' table ready (includes usernames)")

        # Create indexes for better performance
        print("📊 Creating database indexes...")
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_mod_cases_guild_user
            ON moderation_cases(guild_id, user_id)''')
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_mod_cases_created
            ON moderation_cases(created_at)''')
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_mod_warnings_guild_user
            ON moderation_warnings(guild_id, user_id)''')
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_mod_notes_guild_user
            ON moderation_notes(guild_id, user_id)''')
        print("✅ All indexes created")

        conn.commit()
        print("✅ Database changes committed")
        cur.close()
        return_db_connection(conn)

        print("=" * 60)
        print("✅ MODERATION DATABASE INITIALIZED SUCCESSFULLY")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("⚠️  Moderation tracking features will be disabled.")
        return False


# ============================================================================
# MODERATION CASE FUNCTIONS
# ============================================================================

def create_mod_case(guild_id: int, user_id: int, moderator_id: int,
                    action_type: str, reason: str = None,
                    user_name: str = None, moderator_name: str = None) -> Optional[int]:
    """
    Create a new moderation case

    Args:
        guild_id: Discord guild ID
        user_id: Target user ID
        moderator_id: Moderator user ID
        action_type: Type of action (kick, ban, mute, etc.)
        reason: Reason for the action
        user_name: Target username for logging
        moderator_name: Moderator username for logging

    Returns:
        case_id if successful, None otherwise
    """
    if db_pool is None:
        print("⚠️  Database pool not initialized - skipping case creation")
        return None

    try:
        print(f"💾 [DATABASE] Creating moderation case...")
        print(f"   📋 Action: {action_type.upper()}")
        print(f"   👤 Target: {user_name or 'Unknown'} (ID: {user_id})")
        print(f"   👮 Moderator: {moderator_name or 'Unknown'} (ID: {moderator_id})")
        print(f"   📝 Reason: {reason or 'No reason provided'}")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''INSERT INTO moderation_cases
                       (guild_id, user_id, moderator_id, action_type, reason,
                        user_name, moderator_name)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING case_id''',
                    (guild_id, user_id, moderator_id, action_type, reason,
                     user_name, moderator_name))

        case_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return_db_connection(conn)

        print(f"✅ [DATABASE] Successfully created case #{case_id}")
        print(f"   🎯 Case ID: #{case_id}")
        print(f"   ⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        return case_id

    except Exception as e:
        print(f"❌ [DATABASE] Error creating mod case: {type(e).__name__}")
        print(f"   💥 Details: {e}")
        if conn:
            conn.rollback()
            return_db_connection(conn)
        return None


def get_mod_case(case_id: int, guild_id: int) -> Optional[Dict]:
    """Get details of a specific moderation case"""
    if db_pool is None:
        return None

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute('''SELECT *
                       FROM moderation_cases
                       WHERE case_id = %s
                         AND guild_id = %s''',
                    (case_id, guild_id))

        result = cur.fetchone()
        cur.close()
        return_db_connection(conn)

        return dict(result) if result else None

    except Exception as e:
        print(f"❌ Error getting mod case: {e}")
        return None


def update_mod_case_reason(case_id: int, guild_id: int, new_reason: str) -> bool:
    """Update the reason for a moderation case"""
    if db_pool is None:
        return False

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''UPDATE moderation_cases
                       SET reason     = %s,
                           updated_at = CURRENT_TIMESTAMP
                       WHERE case_id = %s
                         AND guild_id = %s''',
                    (new_reason, case_id, guild_id))

        rows_affected = cur.rowcount
        conn.commit()
        cur.close()
        return_db_connection(conn)

        return rows_affected > 0

    except Exception as e:
        print(f"❌ Error updating mod case: {e}")
        if conn:
            conn.rollback()
            return_db_connection(conn)
        return False


def get_user_mod_cases(guild_id: int, user_id: int, limit: int = 10) -> List[Dict]:
    """Get moderation cases for a specific user"""
    if db_pool is None:
        return []

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute('''SELECT *
                       FROM moderation_cases
                       WHERE guild_id = %s
                         AND user_id = %s
                       ORDER BY created_at DESC LIMIT %s''',
                    (guild_id, user_id, limit))

        rows = cur.fetchall()
        cur.close()
        return_db_connection(conn)

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"❌ Error getting user mod cases: {e}")
        return []


# ============================================================================
# WARNING FUNCTIONS
# ============================================================================

def add_warning(guild_id: int, user_id: int, moderator_id: int, reason: str,
                user_name: str = None, moderator_name: str = None) -> Optional[int]:
    """Add a warning to a user"""
    if db_pool is None:
        print("⚠️  Database pool not initialized - skipping warning creation")
        return None

    try:
        print(f"⚠️  [DATABASE] Creating warning...")
        print(f"   👤 Target: {user_name or 'Unknown'} (ID: {user_id})")
        print(f"   👮 Moderator: {moderator_name or 'Unknown'} (ID: {moderator_id})")
        print(f"   📝 Reason: {reason}")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''INSERT INTO moderation_warnings
                           (guild_id, user_id, moderator_id, reason, user_name, moderator_name)
                       VALUES (%s, %s, %s, %s, %s, %s) RETURNING warning_id''',
                    (guild_id, user_id, moderator_id, reason, user_name, moderator_name))

        warning_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return_db_connection(conn)

        print(f"✅ [DATABASE] Successfully created warning #{warning_id}")
        print(f"   🎯 Warning ID: #{warning_id}")
        print(f"   ⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        return warning_id

    except Exception as e:
        print(f"❌ [DATABASE] Error adding warning: {type(e).__name__}")
        print(f"   💥 Details: {e}")
        if conn:
            conn.rollback()
            return_db_connection(conn)
        return None


def get_user_warnings(guild_id: int, user_id: int) -> List[Dict]:
    """Get all warnings for a specific user"""
    if db_pool is None:
        print("⚠️  Database pool not initialized - cannot fetch warnings")
        return []

    try:
        print(f"🔍 [DATABASE] Fetching warnings for user ID {user_id}...")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute('''SELECT *
                       FROM moderation_warnings
                       WHERE guild_id = %s
                         AND user_id = %s
                       ORDER BY created_at DESC''',
                    (guild_id, user_id))

        rows = cur.fetchall()
        cur.close()
        return_db_connection(conn)

        print(f"✅ [DATABASE] Found {len(rows)} warning(s)")
        return [dict(row) for row in rows]

    except Exception as e:
        print(f"❌ [DATABASE] Error getting warnings: {type(e).__name__}")
        print(f"   💥 Details: {e}")
        return []


def clear_user_warnings(guild_id: int, user_id: int, user_name: str = None) -> int:
    """Clear all warnings for a user, returns number of warnings cleared"""
    if db_pool is None:
        print("⚠️  Database pool not initialized - cannot clear warnings")
        return 0

    try:
        print(f"🗑️  [DATABASE] Clearing warnings for {user_name or 'Unknown'} (ID: {user_id})...")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''DELETE
                       FROM moderation_warnings
                       WHERE guild_id = %s
                         AND user_id = %s''',
                    (guild_id, user_id))

        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        return_db_connection(conn)

        print(f"✅ [DATABASE] Cleared {deleted_count} warning(s)")
        print(f"   👤 User: {user_name or 'Unknown'} (ID: {user_id})")
        print(f"   ⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        return deleted_count

    except Exception as e:
        print(f"❌ [DATABASE] Error clearing warnings: {type(e).__name__}")
        print(f"   💥 Details: {e}")
        if conn:
            conn.rollback()
            return_db_connection(conn)
        return 0


# ============================================================================
# MODERATION NOTE FUNCTIONS
# ============================================================================

def add_mod_note(guild_id: int, user_id: int, moderator_id: int, note_text: str,
                 user_name: str = None, moderator_name: str = None) -> Optional[int]:
    """Add a moderation note (visible only to moderators)"""
    if db_pool is None:
        print("⚠️  Database pool not initialized - skipping note creation")
        return None

    try:
        print(f"📝 [DATABASE] Creating moderation note...")
        print(f"   👤 Target: {user_name or 'Unknown'} (ID: {user_id})")
        print(f"   👮 Moderator: {moderator_name or 'Unknown'} (ID: {moderator_id})")
        print(f"   📄 Note: {note_text[:50]}{'...' if len(note_text) > 50 else ''}")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''INSERT INTO moderation_notes
                           (guild_id, user_id, moderator_id, note_text, user_name, moderator_name)
                       VALUES (%s, %s, %s, %s, %s, %s) RETURNING note_id''',
                    (guild_id, user_id, moderator_id, note_text, user_name, moderator_name))

        note_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return_db_connection(conn)

        print(f"✅ [DATABASE] Successfully created note #{note_id}")
        print(f"   🎯 Note ID: #{note_id}")
        print(f"   ⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        return note_id

    except Exception as e:
        print(f"❌ [DATABASE] Error adding mod note: {type(e).__name__}")
        print(f"   💥 Details: {e}")
        if conn:
            conn.rollback()
            return_db_connection(conn)
        return None


def get_user_mod_notes(guild_id: int, user_id: int) -> List[Dict]:
    """Get all moderation notes for a specific user"""
    if db_pool is None:
        print("⚠️  Database pool not initialized - cannot fetch notes")
        return []

    try:
        print(f"🔍 [DATABASE] Fetching mod notes for user ID {user_id}...")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute('''SELECT *
                       FROM moderation_notes
                       WHERE guild_id = %s
                         AND user_id = %s
                       ORDER BY created_at DESC''',
                    (guild_id, user_id))

        rows = cur.fetchall()
        cur.close()
        return_db_connection(conn)

        print(f"✅ [DATABASE] Found {len(rows)} note(s)")
        return [dict(row) for row in rows]

    except Exception as e:
        print(f"❌ [DATABASE] Error getting mod notes: {type(e).__name__}")
        print(f"   💥 Details: {e}")
        return []


def delete_mod_note(note_id: int, guild_id: int) -> bool:
    """Delete a moderation note"""
    if db_pool is None:
        return False

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''DELETE
                       FROM moderation_notes
                       WHERE note_id = %s
                         AND guild_id = %s''',
                    (note_id, guild_id))

        rows_affected = cur.rowcount
        conn.commit()
        cur.close()
        return_db_connection(conn)

        return rows_affected > 0

    except Exception as e:
        print(f"❌ Error deleting mod note: {e}")
        if conn:
            conn.rollback()
            return_db_connection(conn)
        return False


# ============================================================================
# CLEANUP FUNCTION
# ============================================================================

def close_database():
    """
    Close all database connections and clean up the connection pool.
    Called when the bot shuts down.
    """
    global db_pool

    try:
        if db_pool is None:
            print("✅ No database pool to close")
            return

        # Close all connections in the pool
        db_pool.closeall()
        print("✅ All database connections closed successfully")

    except Exception as e:
        print(f"❌ Error closing database connections: {e}")


# ============================================================================
# CLEANUP FUNCTION
# ============================================================================


# ============================================================================
# END OF DATABASE FUNCTIONS
# ============================================================================
# Remember to:
# 1. Add SUPABASE_URL to your .env file
# 2. Call init_moderation_database() in the on_ready event
# 3. Call close_database() in the finally block of __main__
# ============================================================================
# End Initalization


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True  # Add this line
bot = commands.Bot(command_prefix='!', intents=intents)


def close_database():
    """
    Close all database connections and clean up the connection pool.
    Called when the bot shuts down.
    """
    global db_pool

    try:
        if db_pool is None:
            print("✅ No database pool to close")
            return

        # Close all connections in the pool
        db_pool.closeall()
        print("✅ All database connections closed successfully")

    except Exception as e:
        print(f"❌ Error closing database connections: {e}")

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
STATS_USER = os.getenv('STATS_USER', 'admin')
STATS_PASS = os.getenv('STATS_PASS', 'changeme')
# Supabase Database URL (will be loaded from .env)
SUPABASE_URL = os.getenv('SUPABASE_URL')


# Connection pool for database
db_pool = None


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


def check_auth(request):
    """Check if the request has valid basic auth credentials"""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Basic '):
        return False

    try:
        encoded = auth_header[6:]
        decoded = base64.b64decode(encoded).decode('utf-8')
        username, password = decoded.split(':', 1)
        return username == STATS_USER and password == STATS_PASS
    except:
        return False


def require_auth_response():
    """Return a 401 response requiring authentication"""
    return web.Response(
        text='Authentication Required',
        status=401,
        headers={'WWW-Authenticate': 'Basic realm="Stats Access"'}
    )


@bot.event
async def setup_hook():
    """Runs before bot connects - starts web server immediately"""
    print(f"[{datetime.now()}] Running setup_hook...", flush=True)
    await start_web_server()


async def health_check(request):
    global bot_updating, bot_emergency_shutdown, bot_owner_sleeping
    # Add this line at the top

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
                    🔴 The bot has gone into the deep. Please check back later.
                </div>
                <a href="https://github.com/soryntech/discord-moderation-bot-" target="_blank" class="github-button">
                    🔗 View on GitHub
                </a>
                <a href="https://stats.uptimerobot.com/EfwZKYIE1Q" target="_blank" class="github-button" style="margin-top: 10px;">
                    📊 Uptime Robot Status
                </a>
                <p style="margin-top: 20px; font-size: 0.85em; color: #7eb8d6;">🦈 SorynTech Bot Suite</p>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html', status=503)

    # Check if owner is sleeping
    if bot_owner_sleeping:
        uptime = datetime.now() - bot_start_time
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
                <a href="https://github.com/soryntech/discord-moderation-bot-" target="_blank" class="github-button">
                    🔗 View on GitHub
                </a>
                <a href="https://stats.uptimerobot.com/EfwZKYIE1Q" target="_blank" class="github-button" style="margin-top: 10px;">
                    📊 Uptime Robot Status
                </a>
                <p style="margin-top: 20px; font-size: 0.85em; color: #7eb8d6;">🦈 SorynTech Bot Suite</p>
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
                    ⚠️ SorynTech is performing maintenance on the bot. Check back Later.
                </div>
                <a href="https://github.com/soryntech/discord-moderation-bot-" target="_blank" class="github-button">
                    🔗 View on GitHub
                </a>
                <a href="https://stats.uptimerobot.com/EfwZKYIE1Q" target="_blank" class="github-button" style="margin-top: 10px;">
                    📊 Uptime Robot Status
                </a>
                <p style="margin-top: 20px; font-size: 0.85em; color: #7eb8d6;">🦈 SorynTech Bot Suite</p>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html', status=503)

    # Normal status (bot is running)
    uptime = datetime.now() - bot_start_time
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
            <a href="https://github.com/soryntech/discord-moderation-bot-" target="_blank" class="github-button">
                🔗 View on GitHub
            </a>
            <a href="https://stats.uptimerobot.com/EfwZKYIE1Q" target="_blank" class="github-button" style="margin-top: 10px;">
                📊 Uptime Robot Status
            </a>
            <p style="margin-top: 20px; font-size: 0.85em; color: #7eb8d6;">🦈 SorynTech Bot Suite</p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def stats_page(request):
    """Password-protected detailed stats page"""
    # Check authentication
    if not check_auth(request):
        return require_auth_response()

    # Calculate uptime
    uptime = datetime.now() - bot_start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Get guild list
    guild_list = "\n".join([f"                <li>{guild.name} ({guild.member_count} members)</li>"
                            for guild in bot.guilds])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SorynTech Bot Statistics</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="30">
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
                padding: 20px;
                color: #e0f7ff;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                padding: 40px 20px;
                background: rgba(0, 60, 100, 0.9);
                border-radius: 20px;
                margin-bottom: 30px;
                border: 2px solid rgba(0, 200, 255, 0.3);
            }}
            h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 0 0 10px rgba(0, 200, 255, 0.5);
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: rgba(0, 60, 100, 0.9);
                border-radius: 15px;
                padding: 25px;
                border: 2px solid rgba(0, 200, 255, 0.3);
            }}
            .stat-card h2 {{
                color: #00ddff;
                margin-bottom: 15px;
                font-size: 1.3em;
            }}
            .stat-item {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid rgba(0, 200, 255, 0.1);
            }}
            .stat-item:last-child {{
                border-bottom: none;
            }}
            .stat-label {{
                color: #7eb8d6;
            }}
            .stat-value {{
                color: #00ff88;
                font-weight: bold;
            }}
            .guild-list {{
                background: rgba(0, 60, 100, 0.9);
                border-radius: 15px;
                padding: 25px;
                border: 2px solid rgba(0, 200, 255, 0.3);
            }}
            .guild-list h2 {{
                color: #00ddff;
                margin-bottom: 15px;
            }}
            .guild-list ul {{
                list-style-position: inside;
                color: #7eb8d6;
            }}
            .guild-list li {{
                padding: 8px 0;
                border-bottom: 1px solid rgba(0, 200, 255, 0.1);
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                color: #7eb8d6;
            }}
            .refresh-note {{
                background: rgba(0, 100, 150, 0.3);
                padding: 10px;
                border-radius: 8px;
                display: inline-block;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🦈 SorynTech Bot Statistics</h1>
                <p>Detailed Bot Analytics & Monitoring</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h2>📊 General Stats</h2>
                    <div class="stat-item">
                        <span class="stat-label">Bot Name</span>
                        <span class="stat-value">{bot.user.name if bot.user else "Loading..."}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Bot ID</span>
                        <span class="stat-value">{bot.user.id if bot.user else "Loading..."}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Total Guilds</span>
                        <span class="stat-value">{len(bot.guilds)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Total Users</span>
                        <span class="stat-value">{sum(g.member_count for g in bot.guilds)}</span>
                    </div>
                </div>

                <div class="stat-card">
                    <h2>⏱️ Uptime & Performance</h2>
                    <div class="stat-item">
                        <span class="stat-label">Uptime</span>
                        <span class="stat-value">{days}d {hours}h {minutes}m {seconds}s</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Latency</span>
                        <span class="stat-value">{round(bot.latency * 1000)}ms</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Started At</span>
                        <span class="stat-value">{bot_start_time.strftime('%Y-%m-%d %H:%M UTC')}</span>
                    </div>
                </div>

                <div class="stat-card">
                    <h2>🔧 Bot Status</h2>
                    <div class="stat-item">
                        <span class="stat-label">Emergency Shutdown</span>
                        <span class="stat-value">{'🔴 Active' if bot_emergency_shutdown else '🟢 Normal'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Update Mode</span>
                        <span class="stat-value">{'🟡 Active' if bot_updating else '🟢 Normal'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Owner Sleep Mode</span>
                        <span class="stat-value">{'😴 Active' if bot_owner_sleeping else '🟢 Awake'}</span>
                    </div>
                </div>
            </div>

            <div class="guild-list">
                <h2>🏝️ Connected Servers ({len(bot.guilds)})</h2>
                <ul>
{guild_list}
                </ul>
            </div>

            <div class="footer">
                <p>🦈 SorynTech Bot Suite - Shark Moderation Bot</p>
                <div class="refresh-note">⟳ Auto-refreshing every 30 seconds</div>
                <p style="margin-top: 10px; font-size: 0.9em;">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def start_web_server():
    print(f"[{datetime.now()}] Starting web server on port {PORT}...", flush=True)
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/stats', stats_page)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f'[{datetime.now()}] ✅ Web server started on port {PORT}', flush=True)
    print(f'[{datetime.now()}] 📊 Stats page: http://0.0.0.0:{PORT}/stats (requires auth)', flush=True)


@bot.event
async def on_ready():
    global bot_start_time, commands_synced
    bot_start_time = datetime.now()
    print(f'[{datetime.now()}] {bot.user} has connected to Discord!', flush=True)

    if not commands_synced:
        try:
            print("Attempting to sync commands...")
            synced = await bot.tree.sync()
            commands_synced = True
            print(f"✅ Successfully synced {len(synced)} command(s)")
        except discord.HTTPException as e:
            if e.status == 429:
                print(f"⚠️ Rate limited when syncing commands. Will retry automatically.")
                retry_after = e.response.headers.get('Retry-After', 60)
                print(f"Retry after: {retry_after} seconds")
            else:
                print(f"❌ Failed to sync commands (HTTP error): {e}")
                print(f"Status: {e.status}")
                print(f"Response: {e.text}")
        except Exception as e:
            print(f"❌ Failed to sync commands (unexpected error): {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Commands already synced, skipping sync")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


async def check_emergency_shutdown(interaction: discord.Interaction) -> bool:
    global bot_emergency_shutdown

    if interaction.user.id == 447812883158532106:
        return True

    if bot_emergency_shutdown:
        await interaction.response.send_message(
            "🔴 **Bot is currently offline due to emergency shutdown.**",
            ephemeral=True
        )
        return False

    return True


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    elif isinstance(error, discord.HTTPException):
        if error.status == 429:
            print(f"⚠️ Rate limited! Response: {error.text}")
            await ctx.send("⚠️ Bot is being rate limited. Please wait a moment.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    elif isinstance(error, discord.HTTPException):
        if error.status == 429:
            print(f"⚠️ Rate limited! Response: {error.text}")
            await ctx.send("⚠️ Bot is being rate limited. Please wait a moment.")

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
    # Add delay to prevent rate limiting
    await asyncio.sleep(0.5)

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
    await asyncio.sleep(0.5)

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
    await asyncio.sleep(0.5)

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
    await asyncio.sleep(0.5)

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
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.followup.send("❌ I don't have permission!", ephemeral=True)
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot unmute this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    if member.timed_out_until is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not currently muted!",
            ephemeral=True
        )
        return

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

    if not interaction.guild.me.guild_permissions.move_members:
        await interaction.response.send_message("❌ I don't have permission to move members!", ephemeral=True)
        return

    if member.voice is None or member.voice.channel is None:
        await interaction.response.send_message(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            "❌ I cannot disconnect this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

    try:
        await interaction.response.defer()
        await asyncio.sleep(0.5)
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
    await asyncio.sleep(0.3)
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
    await asyncio.sleep(0.3)
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
    await asyncio.sleep(0.5)

    member = member or interaction.user

    embed = discord.Embed(
        title=f"User Info - {member}",
        color=member.color
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)

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

    roles = [role.mention for role in member.roles[1:]]
    if roles:
        embed.add_field(name="Roles", value=", ".join(roles), inline=False)

    mod_history = []
    try:
        if not interaction.guild.me.guild_permissions.view_audit_log:
            embed.add_field(name="📋 Moderation History", value="⚠️ Bot lacks permission to view audit logs",
                            inline=False)
        else:
            async for entry in interaction.guild.audit_logs(limit=200):
                if not entry.target:
                    continue

                target_id = None
                if hasattr(entry.target, 'id'):
                    target_id = entry.target.id
                elif isinstance(entry.target, int):
                    target_id = entry.target

                if target_id != member.id:
                    continue

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
                    try:
                        before_timeout = getattr(entry.before, 'timed_out_until', None)
                        after_timeout = getattr(entry.after, 'timed_out_until', None)

                        if before_timeout != after_timeout and after_timeout is not None:
                            timestamp = entry.created_at.strftime("%Y-%m-%d %H:%M")
                            moderator = entry.user.mention if entry.user else "Unknown"
                            reason = entry.reason or "No reason provided"
                            mod_history.append(f"⏱️ **Timeout** - {timestamp}\nBy: {moderator}\nReason: {reason}")
                    except AttributeError:
                        pass

            if mod_history:
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
        print(f"Audit log error: {type(e).__name__}: {str(e)}")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="server-deafen", description="Deafen a user")
@app_commands.describe(member="The member to deafen")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_deaf(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.deafen_members:
        await interaction.followup.send("❌ I don't have permission to deafen members!", ephemeral=True)
        return

    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    if member.voice.deaf:
        await interaction.followup.send(
            f"❌ {member.mention} is already server deafened!",
            ephemeral=True
        )
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot deafen this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

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


@bot.tree.command(name="server-mute", description="Mute a user")
@app_commands.describe(member="The member to mute")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_servermute(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.mute_members:
        await interaction.followup.send("I dont have permissions :angry_face:")
        return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send("Member role is too high or my role is too low")
        return

    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

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


@bot.tree.command(name="server-unmute", description="Unmute a user from voice")
@app_commands.describe(member="The member to unmute")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_unmute_voice(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.mute_members:
        await interaction.followup.send("❌ I don't have permission to mute/unmute members!", ephemeral=True)
        return

    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    if not member.voice.mute:
        await interaction.followup.send(
            f"❌ {member.mention} is not server muted!",
            ephemeral=True
        )
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot unmute this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

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


@bot.tree.command(name="server-undeafen", description="Undeafen a user from voice")
@app_commands.describe(member="The member to undeafen")
@app_commands.checks.has_permissions(send_polls=True)
async def slash_undeaf_voice(interaction: discord.Interaction, member: discord.Member):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.deafen_members:
        await interaction.followup.send("❌ I don't have permission to deafen/undeafen members!", ephemeral=True)
        return

    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send(
            f"❌ {member.mention} is not in a voice channel!",
            ephemeral=True
        )
        return

    if not member.voice.deaf:
        await interaction.followup.send(
            f"❌ {member.mention} is not server deafened!",
            ephemeral=True
        )
        return

    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send(
            "❌ I cannot undeafen this member (their role is equal or higher than mine)!",
            ephemeral=True
        )
        return

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
    await asyncio.sleep(0.5)

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

        for channel in interaction.guild.text_channels:
            try:
                await channel.set_permissions(
                    interaction.guild.default_role,
                    send_messages=False,
                    reason=f"Server lockdown by {interaction.user}"
                )
                locked_count += 1
                await asyncio.sleep(0.3)  # Delay between channel locks
            except discord.Forbidden:
                failed_channels.append(channel.name)
            except discord.HTTPException:
                failed_channels.append(channel.name)

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

    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    bot_emergency_shutdown = not bot_emergency_shutdown

    if bot_emergency_shutdown:
        await bot.change_presence(status=discord.Status.invisible)
        await interaction.response.send_message(
            "🔴 **EMERGENCY SHUTDOWN ACTIVATED**\n"
            "All commands are now disabled except /restart-bot.\n"
            "The status page now shows the bot as offline.\n"
            "Bot status set to invisible.",
            ephemeral=True
        )
    else:
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

    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

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


@bot.tree.command(name="update-mode", description="Toggle update mode for the bot status page (Owner Only)")
async def slash_updatemode(interaction: discord.Interaction):
    global bot_updating

    if interaction.user.id != 447812883158532106:
        await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
        return

    bot_updating = not bot_updating

    if bot_updating:
        await bot.change_presence(status=discord.Status.idle)
        await interaction.response.send_message(
            "🔄 **UPDATE MODE ENABLED**\n"
            "The status page now displays 'Shark Bot is Updating'.\n"
            "Bot status set to idle.\n"
            "Use this command again to disable update mode.",
            ephemeral=True
        )
    else:
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

        for channel in interaction.guild.text_channels:
            try:
                await channel.set_permissions(
                    interaction.guild.default_role,
                    send_messages=None,
                    reason=f"Server unlocked by {interaction.user}"
                )
                unlocked_count += 1
                await asyncio.sleep(0.3)  # Delay between channel unlocks
            except discord.Forbidden:
                failed_channels.append(channel.name)
            except discord.HTTPException:
                failed_channels.append(channel.name)

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
    await asyncio.sleep(0.5)

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
    await asyncio.sleep(0.3)

    guild = interaction.guild

    online = sum(1 for m in guild.members if m.status == discord.Status.online)
    idle = sum(1 for m in guild.members if m.status == discord.Status.idle)
    dnd = sum(1 for m in guild.members if m.status == discord.Status.dnd)
    offline = sum(1 for m in guild.members if m.status == discord.Status.offline)

    bots = sum(1 for m in guild.members if m.bot)
    humans = len(guild.members) - bots

    embed = discord.Embed(
        title=f"📊 {guild.name} Server Information",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)

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

    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)

    embed.add_field(
        name="Channels",
        value=f"💬 Text: {text_channels}\n🔊 Voice: {voice_channels}\n📁 Categories: {categories}",
        inline=True
    )

    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
    embed.add_field(name="Boosts", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)",
                    inline=True)

    embed.add_field(name="Verification Level", value=str(guild.verification_level).title(), inline=True)

    if guild.features:
        features = ", ".join([f.replace("_", " ").title() for f in guild.features[:5]])
        if len(guild.features) > 5:
            features += f" (+{len(guild.features) - 5} more)"
        embed.add_field(name="Features", value=features, inline=False)

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="addrole", description="Add a role to a user")
async def slash_addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not await check_emergency_shutdown(interaction):
        return

    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message("I don't have permission to manage roles!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to manage roles!", ephemeral=True)
        return

    if interaction.guild.me.top_role <= role:
        await interaction.response.send_message(
            f"I cannot add {role.mention} because it's higher than or equal to my highest role!", ephemeral=True)
        return

    if interaction.user.top_role <= role and interaction.user != interaction.guild.owner:
        await interaction.response.send_message(
            f"You cannot add {role.mention} because it's higher than or equal to your highest role!", ephemeral=True)
        return

    if role in member.roles:
        await interaction.response.send_message(f"{member.mention} already has the {role.mention} role!",
                                                ephemeral=True)
        return

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

    member_count = len(role.members)

    embed = discord.Embed(
        title="📊 Role Statistics",
        color=role.color
    )

    embed.add_field(name="Role", value=role.mention, inline=True)
    embed.add_field(name="Member Count", value=f"**{member_count}**", inline=True)
    embed.add_field(name="Role ID", value=f"`{role.id}`", inline=False)

    embed.set_footer(text=f"Requested by {interaction.user.name}")
    embed.timestamp = interaction.created_at

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="membercount", description="Display server member statistics")
async def slash_membercount(interaction: discord.Interaction):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.3)

    guild = interaction.guild

    # Count member statuses
    online = sum(1 for m in guild.members if m.status == discord.Status.online)
    idle = sum(1 for m in guild.members if m.status == discord.Status.idle)
    dnd = sum(1 for m in guild.members if m.status == discord.Status.dnd)
    offline = sum(1 for m in guild.members if m.status == discord.Status.offline)

    # Count bots vs humans
    bots = sum(1 for m in guild.members if m.bot)
    humans = len(guild.members) - bots

    embed = discord.Embed(
        title=f"👥 {guild.name} Member Statistics",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(
        name="📊 Total Members",
        value=f"**{len(guild.members)}**",
        inline=False
    )

    embed.add_field(
        name="👤 Member Types",
        value=f"Humans: **{humans}**\nBots: **{bots}**",
        inline=True
    )

    embed.add_field(
        name="📱 Member Status",
        value=f"🟢 Online: **{online}**\n🟡 Idle: **{idle}**\n🔴 DND: **{dnd}**\n⚫ Offline: **{offline}**",
        inline=True
    )

    embed.set_footer(text=f"Requested by {interaction.user.name}")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="botinfo", description="Display bot statistics and information")
async def slash_botinfo(interaction: discord.Interaction):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.3)

    # Calculate uptime
    uptime = datetime.now() - bot_start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Calculate total users across all servers
    total_users = sum(guild.member_count for guild in bot.guilds)

    embed = discord.Embed(
        title="🤖 Bot Information",
        description="SorynTech's Shark Moderation Bot",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)

    embed.add_field(
        name="📊 Bot Stats",
        value=f"Servers: **{len(bot.guilds)}**\nTotal Users: **{total_users}**\nLatency: **{round(bot.latency * 1000)}ms**",
        inline=True
    )

    embed.add_field(
        name="⏱️ Uptime",
        value=f"**{days}**d **{hours}**h **{minutes}**m **{seconds}**s",
        inline=True
    )

    embed.add_field(
        name="🔧 Status",
        value=f"Emergency: {'🔴 Active' if bot_emergency_shutdown else '🟢 Normal'}\nUpdate Mode: {'🟡 Active' if bot_updating else '🟢 Normal'}\nOwner Sleep: {'😴 Active' if bot_owner_sleeping else '🟢 Awake'}",
        inline=False
    )

    embed.add_field(
        name="📝 Bot Info",
        value=f"Bot Name: **{bot.user.name}**\nBot ID: `{bot.user.id}`\nPrefix: `!`",
        inline=False
    )

    embed.add_field(
        name="🔗 Links",
        value="[GitHub](https://github.com/soryntech/discord-moderation-bot-) | [Uptime Status](https://stats.uptimerobot.com/EfwZKYIE1Q)",
        inline=False
    )

    embed.set_footer(text=f"Created by SorynTech • Requested by {interaction.user.name}")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="removerole", description="Remove a role from a user")
@app_commands.describe(
    member="The member to remove role from",
    role="The role to remove"
)
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.followup.send("❌ I don't have permission to manage roles!", ephemeral=True)
        return

    if interaction.guild.me.top_role <= role:
        await interaction.followup.send(
            f"❌ I cannot remove {role.mention} because it's higher than or equal to my highest role!",
            ephemeral=True
        )
        return

    if interaction.user.top_role <= role and interaction.user != interaction.guild.owner:
        await interaction.followup.send(
            f"❌ You cannot remove {role.mention} because it's higher than or equal to your highest role!",
            ephemeral=True
        )
        return

    if role not in member.roles:
        await interaction.followup.send(
            f"❌ {member.mention} doesn't have the {role.mention} role!",
            ephemeral=True
        )
        return

    try:
        await member.remove_roles(role, reason=f"Role removed by {interaction.user}")
        await interaction.followup.send(f"✅ Successfully removed {role.mention} from {member.mention}!")
    except discord.Forbidden:
        await interaction.followup.send("❌ Failed to remove role due to permission issues!", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)


@bot.tree.command(name="createrole", description="Create a new role with specified permissions")
@app_commands.describe(
    name="Name of the new role",
    color="Color in hex format (e.g., #FF5733) - optional",
    hoist="Whether to display role separately in member list",
    mentionable="Whether the role can be mentioned"
)
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_createrole(interaction: discord.Interaction, name: str, color: str = None, hoist: bool = False, mentionable: bool = False):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.followup.send("❌ I don't have permission to manage roles!", ephemeral=True)
        return

    # Parse color if provided
    role_color = discord.Color.default()
    if color:
        try:
            # Remove # if present
            color = color.lstrip('#')
            # Convert hex to RGB
            role_color = discord.Color(int(color, 16))
        except ValueError:
            await interaction.followup.send("❌ Invalid color format! Use hex format like #FF5733", ephemeral=True)
            return

    try:
        new_role = await interaction.guild.create_role(
            name=name,
            color=role_color,
            hoist=hoist,
            mentionable=mentionable,
            reason=f"Role created by {interaction.user}"
        )

        embed = discord.Embed(
            title="✅ Role Created Successfully",
            color=new_role.color,
            timestamp=datetime.now()
        )

        embed.add_field(name="Role", value=new_role.mention, inline=True)
        embed.add_field(name="Role ID", value=f"`{new_role.id}`", inline=True)
        embed.add_field(name="Color", value=f"`{str(new_role.color)}`", inline=True)
        embed.add_field(name="Hoisted", value="✅ Yes" if hoist else "❌ No", inline=True)
        embed.add_field(name="Mentionable", value="✅ Yes" if mentionable else "❌ No", inline=True)

        embed.set_footer(text=f"Created by {interaction.user.name}")

        await interaction.followup.send(embed=embed)

    except discord.Forbidden:
        await interaction.followup.send("❌ Failed to create role due to permission issues!", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)


@bot.tree.command(name="deleterole", description="Delete a role")
@app_commands.describe(role="The role to delete")
@app_commands.checks.has_permissions(manage_roles=True)
async def slash_deleterole(interaction: discord.Interaction, role: discord.Role):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.followup.send("❌ I don't have permission to manage roles!", ephemeral=True)
        return

    if interaction.guild.me.top_role <= role:
        await interaction.followup.send(
            f"❌ I cannot delete {role.mention} because it's higher than or equal to my highest role!",
            ephemeral=True
        )
        return

    if interaction.user.top_role <= role and interaction.user != interaction.guild.owner:
        await interaction.followup.send(
            f"❌ You cannot delete {role.mention} because it's higher than or equal to your highest role!",
            ephemeral=True
        )
        return

    # Store role info before deletion
    role_name = role.name
    role_members = len(role.members)

    try:
        await role.delete(reason=f"Role deleted by {interaction.user}")
        await interaction.followup.send(
            f"✅ Successfully deleted role **{role_name}**\n"
            f"📊 The role had **{role_members}** member(s)"
        )
    except discord.Forbidden:
        await interaction.followup.send("❌ Failed to delete role due to permission issues!", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)


@bot.tree.command(name="roleinfo", description="Display information about a role")
@app_commands.describe(role="The role to get information about")
async def slash_roleinfo(interaction: discord.Interaction, role: discord.Role):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.3)

    embed = discord.Embed(
        title=f"📋 Role Information",
        color=role.color,
        timestamp=datetime.now()
    )

    # Basic information
    embed.add_field(name="Role Name", value=role.name, inline=True)
    embed.add_field(name="Role ID", value=f"`{role.id}`", inline=True)
    embed.add_field(name="Color", value=f"`{str(role.color)}`", inline=True)

    # Position and settings
    embed.add_field(name="Position", value=f"**{role.position}**", inline=True)
    embed.add_field(name="Hoisted", value="✅ Yes" if role.hoist else "❌ No", inline=True)
    embed.add_field(name="Mentionable", value="✅ Yes" if role.mentionable else "❌ No", inline=True)

    # Member count
    embed.add_field(name="Members", value=f"**{len(role.members)}**", inline=True)

    # Managed status
    embed.add_field(
        name="Managed",
        value="✅ Yes (Bot/Integration)" if role.managed else "❌ No",
        inline=True
    )

    # Created date
    embed.add_field(
        name="Created On",
        value=role.created_at.strftime("%Y-%m-%d %H:%M UTC"),
        inline=True
    )

    # Key permissions
    key_perms = []
    if role.permissions.administrator:
        key_perms.append("👑 Administrator")
    if role.permissions.manage_guild:
        key_perms.append("⚙️ Manage Server")
    if role.permissions.manage_roles:
        key_perms.append("🎭 Manage Roles")
    if role.permissions.manage_channels:
        key_perms.append("📁 Manage Channels")
    if role.permissions.kick_members:
        key_perms.append("👢 Kick Members")
    if role.permissions.ban_members:
        key_perms.append("🔨 Ban Members")
    if role.permissions.moderate_members:
        key_perms.append("⏱️ Timeout Members")

    if key_perms:
        embed.add_field(
            name="🔑 Key Permissions",
            value="\n".join(key_perms),
            inline=False
        )

    embed.set_footer(text=f"Requested by {interaction.user.name}")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="rolemembers", description="List all members with a specific role")
@app_commands.describe(role="The role to list members for")
async def slash_rolemembers(interaction: discord.Interaction, role: discord.Role):
    if not await check_emergency_shutdown(interaction):
        return

    await interaction.response.defer()
    await asyncio.sleep(0.3)

    members = role.members

    if not members:
        await interaction.followup.send(f"❌ No members have the {role.mention} role!", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"👥 Members with {role.name}",
        description=f"Total: **{len(members)}** member(s)",
        color=role.color,
        timestamp=datetime.now()
    )

    # Split members into chunks of 20 for readability
    chunk_size = 20
    member_chunks = [members[i:i + chunk_size] for i in range(0, len(members), chunk_size)]

    # Display first chunk inline
    first_chunk = member_chunks[0]
    member_list = "\n".join([f"• {member.mention} ({member.name})" for member in first_chunk])

    if len(member_chunks) > 1:
        member_list += f"\n\n*...and {len(members) - len(first_chunk)} more member(s)*"
        member_list += f"\n\n💡 **Tip:** Use `/role-count` for just the count"

    embed.add_field(name="Members", value=member_list, inline=False)
    embed.set_footer(text=f"Requested by {interaction.user.name}")

    await interaction.followup.send(embed=embed)


#================================================ERROR HANDLING=========================================================================================================================
# ============================================================================
# MODERATION TRACKING COMMANDS
# ============================================================================
# PASTE THIS SECTION BEFORE THE ERROR HANDLERS
# (Before the @slash_ban.error and other error handlers section)
# ============================================================================

# ============================================================================
# MODERATION TRACKING COMMANDS
# ============================================================================
# PASTE THIS SECTION BEFORE THE ERROR HANDLERS
# (Before the @slash_ban.error and other error handlers section)
# ============================================================================

@bot.tree.command(name="warn", description="Issue a warning to a user")
@app_commands.describe(
    member="The member to warn",
    reason="Reason for the warning"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Issue a warning to a user and log it in the database"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    # Add warning to database
    warning_id = await asyncio.to_thread(
        add_warning,
        interaction.guild.id,
        member.id,
        interaction.user.id,
        reason,
        member.name,  # Add username
        interaction.user.name  # Add moderator name
    )

    if warning_id is None:
        await interaction.followup.send(
            "❌ Failed to create warning in database.",
            ephemeral=True
        )
        return

    # Get total warnings for this user
    warnings = await asyncio.to_thread(
        get_user_warnings,
        interaction.guild.id,
        member.id
    )

    warning_count = len(warnings)

    # Create embed
    embed = discord.Embed(
        title="⚠️ User Warned",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )

    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Warning ID", value=f"#{warning_id}", inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Total Warnings", value=f"**{warning_count}**", inline=True)

    embed.set_footer(text=f"Use /warnings to view all warnings for this user")

    await interaction.followup.send(embed=embed)

    # Try to DM the user
    try:
        dm_embed = discord.Embed(
            title=f"⚠️ Warning in {interaction.guild.name}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        dm_embed.add_field(name="Moderator", value=interaction.user.name, inline=True)
        dm_embed.add_field(name="Total Warnings", value=f"**{warning_count}**", inline=True)
        dm_embed.add_field(name="Reason", value=reason, inline=False)

        await member.send(embed=dm_embed)
    except discord.Forbidden:
        pass  # User has DMs disabled


@bot.tree.command(name="warnings", description="View all warnings for a user")
@app_commands.describe(member="The member to check warnings for")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_warnings(interaction: discord.Interaction, member: discord.Member):
    """View all warnings for a specific user"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0.3)

    # Get warnings from database
    warnings = await asyncio.to_thread(
        get_user_warnings,
        interaction.guild.id,
        member.id
    )

    if not warnings:
        await interaction.followup.send(
            f"✅ {member.mention} has no warnings on record.",
            ephemeral=True
        )
        return

    # Create embed
    embed = discord.Embed(
        title=f"⚠️ Warnings for {member.name}",
        description=f"Total: **{len(warnings)}** warning(s)",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    # Show up to 5 most recent warnings
    for i, warning in enumerate(warnings[:5], 1):
        # Use stored moderator name, fallback to fetching if not available
        mod_name = warning.get('moderator_name')
        if not mod_name:
            try:
                moderator = await bot.fetch_user(warning['moderator_id'])
                mod_name = moderator.name
            except:
                mod_name = f"Unknown (ID: {warning['moderator_id']})"

        timestamp = warning['created_at'].strftime("%Y-%m-%d %H:%M UTC")

        embed.add_field(
            name=f"Warning #{warning['warning_id']} - {timestamp}",
            value=f"**Moderator:** {mod_name}\n**Reason:** {warning['reason']}",
            inline=False
        )

    if len(warnings) > 5:
        embed.set_footer(text=f"Showing 5 of {len(warnings)} warnings")

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="clearwarnings", description="Clear all warnings for a user")
@app_commands.describe(member="The member to clear warnings for")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_clearwarnings(interaction: discord.Interaction, member: discord.Member):
    """Clear all warnings for a user"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer()
    await asyncio.sleep(0.5)

    # Clear warnings
    cleared_count = await asyncio.to_thread(
        clear_user_warnings,
        interaction.guild.id,
        member.id,
        member.name  # Add username
    )

    if cleared_count == 0:
        await interaction.followup.send(
            f"ℹ️ {member.mention} has no warnings to clear.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="✅ Warnings Cleared",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Warnings Cleared", value=f"**{cleared_count}**", inline=True)

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="case", description="View details of a specific moderation case")
@app_commands.describe(case_id="The case ID number to look up")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_case(interaction: discord.Interaction, case_id: int):
    """View details of a moderation case"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0.3)

    # Get the case from database
    case = await asyncio.to_thread(get_mod_case, case_id, interaction.guild.id)

    if not case:
        await interaction.followup.send(
            f"❌ Case #{case_id} not found in this server.",
            ephemeral=True
        )
        return

    # Try to use stored names, fallback to fetching if not available
    target_name = case.get('user_name')
    if not target_name:
        try:
            target_user = await bot.fetch_user(case['user_id'])
            target_name = f"{target_user.name} ({target_user.mention})"
        except:
            target_name = f"Unknown User (ID: {case['user_id']})"
    else:
        target_name = f"{target_name} (ID: {case['user_id']})"

    mod_name = case.get('moderator_name')
    if not mod_name:
        try:
            moderator = await bot.fetch_user(case['moderator_id'])
            mod_name = f"{moderator.name} ({moderator.mention})"
        except:
            mod_name = f"Unknown Moderator (ID: {case['moderator_id']})"
    else:
        mod_name = f"{mod_name} (ID: {case['moderator_id']})"

    # Create embed
    embed = discord.Embed(
        title=f"📋 Moderation Case #{case_id}",
        color=discord.Color.blue(),
        timestamp=case['created_at']
    )

    embed.add_field(name="Action Type", value=f"**{case['action_type'].title()}**", inline=True)
    embed.add_field(name="Target User", value=target_name, inline=True)
    embed.add_field(name="Moderator", value=mod_name, inline=False)

    reason = case.get('reason') or "No reason provided"
    embed.add_field(name="Reason", value=reason, inline=False)

    if case.get('updated_at') and case['updated_at'] != case['created_at']:
        embed.add_field(
            name="Last Updated",
            value=f"<t:{int(case['updated_at'].timestamp())}:F>",
            inline=False
        )

    embed.set_footer(text=f"Case ID: {case_id} | Created")

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="cases", description="View moderation cases for a user")
@app_commands.describe(
    member="The member to check cases for",
    limit="Number of cases to show (default 5)"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_cases(interaction: discord.Interaction, member: discord.Member, limit: int = 5):
    """View moderation cases for a specific user"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0.3)

    # Get cases from database
    cases = await asyncio.to_thread(
        get_user_mod_cases,
        interaction.guild.id,
        member.id,
        min(limit, 10)  # Cap at 10
    )

    if not cases:
        await interaction.followup.send(
            f"✅ {member.mention} has no moderation cases on record.",
            ephemeral=True
        )
        return

    # Create embed
    embed = discord.Embed(
        title=f"📋 Moderation Cases for {member.name}",
        description=f"Showing up to {len(cases)} most recent case(s)",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    for case in cases:
        # Use stored moderator name, fallback to fetching if not available
        mod_name = case.get('moderator_name')
        if not mod_name:
            try:
                moderator = await bot.fetch_user(case['moderator_id'])
                mod_name = moderator.name
            except:
                mod_name = f"Unknown (ID: {case['moderator_id']})"

        timestamp = case['created_at'].strftime("%Y-%m-%d %H:%M UTC")
        reason = case.get('reason') or "No reason provided"

        embed.add_field(
            name=f"Case #{case['case_id']} - {case['action_type'].title()} - {timestamp}",
            value=f"**Moderator:** {mod_name}\n**Reason:** {reason}",
            inline=False
        )

    embed.set_footer(text=f"Use /case <id> to view full details of a specific case")

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="updatecase", description="Update the reason for a moderation case")
@app_commands.describe(
    case_id="The case ID to update",
    new_reason="The new reason for the case"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_updatecase(interaction: discord.Interaction, case_id: int, new_reason: str):
    """Update the reason for a moderation case"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0.5)

    # Update the case
    success = await asyncio.to_thread(
        update_mod_case_reason,
        case_id,
        interaction.guild.id,
        new_reason
    )

    if not success:
        await interaction.followup.send(
            f"❌ Case #{case_id} not found or could not be updated.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="✅ Case Updated",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
    embed.add_field(name="Updated By", value=interaction.user.mention, inline=True)
    embed.add_field(name="New Reason", value=new_reason, inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="modnote", description="Add a private moderation note to a user")
@app_commands.describe(
    member="The member to add a note for",
    note="The note text (visible only to moderators)"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_modnote(interaction: discord.Interaction, member: discord.Member, note: str):
    """Add a private moderation note to a user"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0.5)

    # Add note to database
    note_id = await asyncio.to_thread(
        add_mod_note,
        interaction.guild.id,
        member.id,
        interaction.user.id,
        note,
        member.name,  # Add username
        interaction.user.name  # Add moderator name
    )

    if note_id is None:
        await interaction.followup.send(
            "❌ Failed to create moderation note.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="📝 Moderation Note Added",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Note ID", value=f"#{note_id}", inline=True)
    embed.add_field(name="Note", value=note, inline=False)

    embed.set_footer(text="This note is only visible to moderators")

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="modnotes", description="View all moderation notes for a user")
@app_commands.describe(member="The member to check notes for")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_modnotes(interaction: discord.Interaction, member: discord.Member):
    """View all moderation notes for a specific user"""
    if not await check_emergency_shutdown(interaction):
        return

    if db_pool is None:
        await interaction.response.send_message(
            "❌ Moderation tracking is not enabled. Contact the bot owner.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0.3)

    # Get notes from database
    notes = await asyncio.to_thread(
        get_user_mod_notes,
        interaction.guild.id,
        member.id
    )

    if not notes:
        await interaction.followup.send(
            f"ℹ️ No moderation notes found for {member.mention}.",
            ephemeral=True
        )
        return

    # Create embed
    embed = discord.Embed(
        title=f"📝 Moderation Notes for {member.name}",
        description=f"Total: **{len(notes)}** note(s)",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    # Show up to 5 most recent notes
    for note in notes[:5]:
        # Use stored moderator name, fallback to fetching if not available
        mod_name = note.get('moderator_name')
        if not mod_name:
            try:
                moderator = await bot.fetch_user(note['moderator_id'])
                mod_name = moderator.name
            except:
                mod_name = f"Unknown (ID: {note['moderator_id']})"

        timestamp = note['created_at'].strftime("%Y-%m-%d %H:%M UTC")

        embed.add_field(
            name=f"Note #{note['note_id']} - {timestamp}",
            value=f"**By:** {mod_name}\n**Note:** {note['note_text']}",
            inline=False
        )

    if len(notes) > 5:
        embed.set_footer(text=f"Showing 5 of {len(notes)} notes | Only visible to moderators")
    else:
        embed.set_footer(text="Only visible to moderators")

    await interaction.followup.send(embed=embed, ephemeral=True)
# Error handling
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
@slash_membercount.error
@slash_botinfo.error
@slash_removerole.error
@slash_createrole.error
@slash_deleterole.error
@slash_roleinfo.error
@slash_rolemembers.error
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
    # Check if message author is a bot
    if ctx.author.bot:
        return

    if not ctx.guild.me.guild_permissions.kick_members:
        await ctx.send("❌ I don't have permission to kick members!")
        return
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ I cannot kick this member (their role is equal or higher than mine)!")
        return
    await asyncio.sleep(0.5)
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} has been kicked. Reason: {reason or 'No reason provided'}")


@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def prefix_ban(ctx, member: discord.Member, *, reason=None):
    # Check if message author is a bot
    if ctx.author.bot:
        return

    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("❌ I don't have permission to ban members!")
        return
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ I cannot ban this member (their role is equal or higher than mine)!")
        return
    await asyncio.sleep(0.5)
    await member.ban(reason=reason)
    await ctx.send(f"✅ {member.mention} has been banned. Reason: {reason or 'No reason provided'}")


if __name__ == "__main__":
    print("=== BOT STARTING ===")
    print(f"TOKEN exists: {bool(TOKEN)}")
    print(f"PORT: {PORT}")
    print(f"STATS_USER: {STATS_USER}")
    print(f"STATS_PASS: {'***' if STATS_PASS else 'Not Set'}")

    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found in environment variables!")
        print("Make sure your .env file contains DISCORD_TOKEN=your_token_here")
    else:
        print("Starting bot...")
        try:
            bot.run(TOKEN, log_handler=None)
        finally:
            close_database()

    print("=== BOT EXITED ===")