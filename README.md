# Discord Moderation Bot - SorynTech's Shark Bot 🦈

A comprehensive Discord moderation bot with an underwater shark-themed status page and powerful moderation features.

## 🌊 Status Page Features

The bot includes a beautiful underwater shark-themed web status page that displays different states:

### Online Status - "Shark is Hunting" 🦈
- Deep ocean blue gradient background
- Animated swimming fish (🐠🐟🐡)
- Green pulsing shark icon
- **Discord Status**: 🟢 Online
- Displays:
  - **Shark Name** (Bot name)
  - **Swim Time** (Uptime)
  - **Ocean Territories** (Server count)
  - **Sonar Ping** (Latency in ms)
- **GitHub Button**: Links to repository

### Emergency Shutdown - "Shark Bot is Offline" 🔴
- Dark deep ocean theme with animated bubbles
- Red pulsing shark icon with warning border
- **Discord Status**: ⚫ Invisible (appears offline)
- **HTTP Status**: 503 Service Unavailable
- All commands blocked except owner commands
- Message: "The bot has gone into the deep"
- **GitHub Button**: Links to repository

### Owner Sleep Mode - "Shark Owner is Sleeping" 💤
- Normal online theme with all bot statistics
- Animated swimming fish (🐠🐟🐡)
- Green pulsing shark icon
- **Discord Status**: 🟢 Online
- **Commands remain fully functional**
- Message: "SorynTech is asleep and isn't looking at PRs on GitHub right now"
- Shows all normal stats (uptime, servers, latency)
- **GitHub Button**: Links to repository

### Update Mode - "Shark Bot is Updating" ⚙️
- Ocean blue with swimming sharks crossing the screen
- Spinning gear icon with orange/amber glow
- **Discord Status**: 🟡 Idle
- **HTTP Status**: 503 Service Unavailable
- Commands remain functional
- Message: "The shark is performing maintenance in the deep"
- **GitHub Button**: Links to repository

All status pages feature:
- Animated water effects and movement
- Glowing text shadows
- Ocean-themed color palettes
- Responsive design for mobile and desktop
- Custom animations (bubbles, fish swimming, seaweed swaying)
- **GitHub repository link button** on every page

---

## 🎮 Command Categories

### 👑 Owner-Only Commands
| Command | Description | Blocks Commands? | Discord Status |
|---------|-------------|------------------|----------------|
| `/killswitch` | Toggle emergency shutdown mode | ✅ Yes - Shows "Offline" | ⚫ Invisible |
| `/restart-bot` | Restart bot from emergency shutdown | N/A | 🟢 Online |
| `/owner-sleep` | Toggle sleep status on status page | ❌ No - Only changes page | 🟢 Online |
| `/updatemode` | Toggle update mode on status page | ❌ No - Only changes page | 🟡 Idle |

### 🔨 Moderation Commands
| Command | Description | Required Permission |
|---------|-------------|---------------------|
| `/kick` | Kick a member from the server | Kick Members |
| `/ban` | Ban a member from the server | Ban Members |
| `/unban` | Unban a user using their ID | Ban Members |
| `/mute` | Timeout a member (in seconds) | Moderate Members |
| `/unmute` | Remove timeout from a member | Moderate Members |
| `/nickname` | Change a member's nickname | Manage Nicknames |

### 🔊 Voice Moderation Commands
| Command | Description | Required Permission |
|---------|-------------|---------------------|
| `/dc` | Disconnect a user from voice | Move Members |
| `/server-deafen` | Server deafen a user in voice | Deafen Members |
| `/server-mute` | Server mute a user in voice | Mute Members |
| `/server-unmute` | Server unmute a user in voice | Mute Members |
| `/server-undeafen` | Server undeafen a user in voice | Deafen Members |

### 💬 Message Management Commands
| Command | Description | Required Permission |
|---------|-------------|---------------------|
| `/purge` | Mass delete messages (max 100) | Manage Messages |

### 🔒 Server Management Commands
| Command | Description | Required Permission |
|---------|-------------|---------------------|
| `/lockdown` | Lock down all text channels | Administrator |
| `/unlockserver` | Unlock all text channels | Administrator |

### 👥 Role Management Commands
| Command | Description | Required Permission |
|---------|-------------|---------------------|
| `/addrole` | Add a role to a user | Manage Roles |
| `/removerole` | Remove a role from a user | Manage Roles |
| `/createrole` | Create a new role with specified permissions | Manage Roles |
| `/deleterole` | Delete a role | Manage Roles |
| `/roleinfo` | Display information about a role | None |
| `/rolemembers` | List all members with a specific role | None |
| `/role-count` | Show how many users have a role | None |

### ℹ️ Information Commands
| Command | Description | Required Permission |
|---------|-------------|---------------------|
| `/userinfo` | Get detailed user information & mod history | Moderate Members |
| `/userpicture` | Get a user's profile picture | Send Messages |
| `/userbanner` | Get a user's nitro banner | Send Messages |
| `/serverinfo` | Display detailed server statistics | None |
| `/membercount` | Display server member statistics | None |
| `/botinfo` | Display bot statistics and information | None |
| `/ping` | Check bot latency | None |

---

## ✅ Completed Commands (40 Total)

### Owner Commands (4)
- [x] `/killswitch` - Emergency bot shutdown with invisible status
- [x] `/restart-bot` - Restart from emergency shutdown
- [x] `/owner-sleep` - Toggle sleep status page
- [x] `/updatemode` - Toggle update mode status page with idle status

### Moderation Commands (6)
- [x] `/kick` - Kick a member from the server
- [x] `/ban` - Ban a member from the server
- [x] `/unban` - Unban a user from the server
- [x] `/mute` - Timeout a member
- [x] `/unmute` - Remove timeout from a member
- [x] `/nickname` - Change a member's nickname

### Voice Moderation (5)
- [x] `/dc` - Disconnect a user from voice
- [x] `/server-deafen` - Server deafen a user in voice
- [x] `/server-mute` - Server mute a user in voice
- [x] `/server-unmute` - Server unmute a user in voice
- [x] `/server-undeafen` - Server undeafen a user in voice

### Message Management (1)
- [x] `/purge` - Mass delete messages

### Server Management (2)
- [x] `/lockdown` - Lock down the entire server
- [x] `/unlockserver` - Unlock all channels after lockdown

### Role Management (7)
- [x] `/addrole` - Give a role to a user
- [x] `/removerole` - Remove a role from a user
- [x] `/createrole` - Create a new role with specified permissions
- [x] `/deleterole` - Delete a role
- [x] `/roleinfo` - Display information about a role
- [x] `/rolemembers` - List all members with a specific role
- [x] `/role-count` - Show how many users have a specific role

### Information Commands (9)
- [x] `/userpicture` - Get a user's profile picture
- [x] `/userbanner` - Get a user's nitro banner
- [x] `/userinfo` - Get detailed information about a user (includes mod history)
- [x] `/serverinfo` - Display detailed server information
- [x] `/membercount` - Display server member statistics
- [x] `/botinfo` - Display bot statistics and information
- [x] `/ping` - Check bot latency

---

## 📋 Planned Commands

### Advanced Message Management
- [ ] `clear` - Delete messages from a specific user
- [ ] `purgebots` - Delete only bot messages
- [ ] `purgeembeds` - Delete messages containing embeds
- [ ] `purgeattachments` - Delete messages with files/images/videos
- [ ] `purgelinks` - Delete messages containing URLs
- [ ] `purgecontains` - Delete messages containing specific word/phrase
- [ ] `purgeuntil` - Delete messages until a specific message ID

### Channel Management
- [ ] `lock` - Lock a specific channel
- [ ] `unlock` - Unlock a specific channel
- [ ] `slowmode` - Set slowmode delay for a channel
- [ ] `nuke` - Clone and delete a channel (clears all messages)
- [ ] `clone` - Clone a channel with same permissions
- [ ] `hide` - Hide a channel from @everyone
- [ ] `unhide` - Unhide a channel

### Utility Commands
- [ ] `uptime` - Show how long the bot has been running
- [ ] `avatar` - Get user's avatar (alternative to userpicture)
- [ ] `invite` - Generate bot invite link
- [ ] `announce` - Send an announcement with embed to a channel
- [ ] `say` - Make the bot say something
- [ ] `embed` - Create a custom embed message
- [ ] `poll` - Create a poll with reactions
- [ ] `commandinfo` - Get command permissions and information 

### Advanced Features
- [ ] `setlogchannel` - Set a channel for mod logs
- [ ] `togglelog` - Enable/disable specific log events
- [ ] `automod` - Toggle automod features (anti-spam, anti-caps, etc.)
### DATABASE FOR MODERATION COMMANDS
- [ ] Integreate to SupaBase DataBase on a new account

---

## 🎨 Key Features

### Status Page
- **Endpoint**: `http://your-bot-url/` or `http://your-bot-url/health`
- **Real-time Status**: Shows current bot state with beautiful underwater theme
- **Multiple States**: Online, Offline (Emergency), Sleeping, Updating
- **Animated Effects**: Swimming fish, bubbles, seaweed, water movement
- **GitHub Integration**: Every status page includes a link to the repository
- **HTTP Status Codes**: 
  - Normal/Sleeping: 200 OK
  - Emergency Shutdown/Update Mode: 503 Service Unavailable

### Discord Presence Status
The bot automatically changes its Discord status based on mode:
- **🟢 Online**: Normal operation and owner sleep mode
- **🟡 Idle**: Update mode (maintenance)
- **⚫ Invisible**: Emergency shutdown (appears offline)

### Error Handling
Comprehensive error handling for all commands:
- Missing permissions (user)
- Bot missing permissions
- Command cooldowns
- Unexpected errors with logging
- User-friendly error messages

### Security Features
- Role hierarchy checks (bot can't moderate users with higher roles)
- Permission verification before actions
- Owner-only commands for critical operations
- Emergency shutdown mode
- Administrator-only access for critical features

### User Information Features
- Detailed user profiles
- Server join/account creation dates
- Role listings
- Current timeout/mute/deafen status
- **Moderation History** (from audit logs):
  - Kicks
  - Bans/Unbans
  - Timeouts
  - Shows moderator, timestamp, and reason

---

## 📊 Progress Statistics
- **Completed:** 40 commands
- **Planned:** 25 commands
- **Total Roadmap:** 65 commands

---

## 🛠️ Technical Details

### Built With
- **discord.py** - Discord API wrapper
- **aiohttp** - Web server for status page
- **Python 3.8+** - Programming language

### Requirements
- Discord Bot Token
- Bot Permissions:
  - Kick Members
  - Ban Members
  - Moderate Members (Timeout)
  - Manage Messages
  - Manage Channels
  - Manage Nicknames
  - Manage Roles
  - Move Members
  - Mute Members
  - Deafen Members
  - View Audit Log (for moderation history)

### Configuration
The bot uses environment variables stored in a `.env` file:
```
DISCORD_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_BOT_URL=your_bot_url_here (optional)
PORT=10000 (optional, defaults to 10000)
STATS_USER=admin (optional, for /stats page)
STATS_PASS=changeme (optional, for /stats page)
```

### Status Page Access
Once the bot is running, access the status page at:
- `http://localhost:10000/` (local development)
- `http://your-deployment-url/` (production)
- `http://your-deployment-url/stats` (detailed stats - password protected)

---

## 🔄 Recent Updates

### January 7, 2026 (Latest)
- ✨ Added 7 new commands (membercount, botinfo, removerole, createrole, deleterole, roleinfo, rolemembers)
- 📊 Enhanced role management with full CRUD operations
- 🎨 New information commands for better server insights
- 📈 Progress: 40/65 commands complete (61.5%)

### December 30, 2025
- 🔧 Added token debug script for troubleshooting without logging in
- 🤖 Debug script fetches bot username directly from Discord API
- 🎨 Updated status page titles: "Shark Bot is Offline" and "Shark Bot is Updating"
- 😴 Modified owner sleep page to show "Shark Owner is Sleeping" with GitHub PR message
- 🔗 Added GitHub repository button to all status pages
- 🎭 Implemented Discord presence status changes:
  - Emergency shutdown → Invisible (appears offline)
  - Update mode → Idle (yellow/orange status)
  - Normal/Sleep mode → Online (green status)

### December 28, 2025
- ✨ Added underwater shark theme to all status pages
- 🎨 Animated effects: swimming fish, bubbles, seaweed
- 🆕 New owner commands: `/killswitch`, `/restart-bot`, `/owner-sleep`, `/updatemode`
- 🔧 Updated `/owner-sleep` to only change status page (commands remain active)
- 🛡️ Enhanced error handling for all commands
- 📊 Added comprehensive command documentation

### Previous Updates
- Added moderation history to `/userinfo`
- Implemented role management commands
- Created server lockdown features
- Added voice moderation commands

---

## 📝 Notes

- **Owner ID** is hardcoded in the bot (User ID: `447812883158532106`)
- All slash commands have proper permission checks
- Bot respects role hierarchy (cannot moderate users with higher roles)
- Audit log access required for moderation history in `/userinfo`
- Status page updates in real-time based on bot state
- Moderation actions attempt to DM users when possible
- **Discord status automatically changes** based on bot mode (Online/Idle/Invisible)
- **GitHub repository link** available on all status pages: https://github.com/soryntech/discord-moderation-bot
- **Debug script available** for token troubleshooting (local use only, not for production servers)

---

## 🤝 Contributing

This is a personal project by SorynTech. If you have suggestions or find bugs, feel free to reach out!

**Repository**: https://github.com/soryntech/discord-moderation-bot

---

## 📄 License

MIT License

Copyright (c) 2025 SorynTech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Made with 💙 by SorynTech** 🦈  
**Last Updated: 7th January 2026**
