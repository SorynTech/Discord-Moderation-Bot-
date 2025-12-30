import os
import base64
import requests

def load_env_file(filepath='.env'):
    """Load variables from .env file into os.environ"""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                # Split on first = sign
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    # Set in os.environ so it's accessible everywhere
                    os.environ[key.strip()] = value

# Load the variables
load_env_file()

TOKEN = os.getenv('DISCORD_TOKEN')

print("=== TOKEN DEBUG ===")
print(f"Token exists: {TOKEN is not None}")
print(f"Token length: {len(TOKEN) if TOKEN else 0}")
print(f"Token first 10 chars: {TOKEN[:10] if TOKEN else 'None'}...")
print(f"Token last 10 chars: ...{TOKEN[-10:] if TOKEN else 'None'}")
print(f"Has spaces: {' ' in TOKEN if TOKEN else 'N/A'}")
has_quotes = ('"' in TOKEN or "'" in TOKEN) if TOKEN else False
print(f"Has quotes: {has_quotes}")

# Get bot username from Discord API without logging in
if TOKEN:
    try:
        response = requests.get('https://discord.com/api/v10/users/@me',
                                headers={'Authorization': f'Bot {TOKEN}'},
                                timeout=10)
        if response.status_code == 200:
            bot_data = response.json()
            print(f"\nBot: {bot_data['username']} (ID: {bot_data['id']})")
        else:
            print(f"\n⚠️  Could not fetch bot info: {response.status_code}")
    except requests.RequestException as e:
        print(f"\n⚠️  Error fetching bot info: {e}")

print("==================")

if TOKEN and len(TOKEN) < 50:
    print("⚠️  WARNING: Token seems too short! Should be 70+ characters")
if TOKEN and ' ' in TOKEN:
    print("⚠️  WARNING: Token contains spaces! Remove them")