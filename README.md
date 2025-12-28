# Discord Moderation Bot - SorynTech's Shark Bot 🦈

A comprehensive Discord moderation bot with an underwater shark-themed status page and powerful moderation features.

## 🌊 Status Page Features

The bot includes a beautiful underwater shark-themed web status page that displays different states:

### Online Status - "Shark is Hunting" 🦈
- Deep ocean blue gradient background
- Animated swimming fish (🐠🐟🐡)
- Green pulsing shark icon
- Displays:
  - **Shark Name** (Bot name)
  - **Swim Time** (Uptime)
  - **Ocean Territories** (Server count)
  - **Sonar Ping** (Latency in ms)

### Emergency Shutdown - "Shark in the Deep" 🔴
- Dark deep ocean theme with animated bubbles
- Red pulsing shark icon with warning border
- All commands blocked except owner commands
- Message: "The bot has gone into the deep"

### Owner Sleep Mode - "Shark is Sleeping" 💤
- Dark blue ocean with swaying seaweed
- Floating shark with sleep emoji (🦈💤)
- **Commands remain fully functional**
- Message: "SorynTech is sleeping and will not respond to any PRs"

### Update Mode - "Shark is Updating" ⚙️
- Ocean blue with swimming sharks crossing the screen
- Spinning gear icon with orange/amber glow
- Commands remain functional
- Message: "The shark is performing maintenance in the deep"

All status pages feature:
- Animated water effects and movement
- Glowing text shadows
- Ocean-themed color palettes
- Responsive design for mobile and desktop
- Custom animations (bubbles, fish swimming, seaweed swaying)

---

## 🎮 Command Categories

### 👑 Owner-Only Commands
| Command | Description | Blocks Commands? |
|---------|-------------|------------------|
| `/killswitch` | Toggle emergency shutdown mode | ✅ Yes - Shows "Offline" |
| `/restart-bot` | Restart bot from emergency shutdown | N/A |
| `/owner-sleep` | Toggle sleep status on status page | ❌ No - Only changes page |
| `/updatemode` | Toggle update mode on status page | ❌ No - Only changes page |

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
| `/sdeaf` | Server deafen a user in voice | Deafen Members |
| `/smute` | Server mute a user in voice | Mute Members |
| `/smuteno` | Server unmute a user in voice | Mute Members |
| `/sdeafno` | Server undeafen a user in voice | Deafen Members |

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
| `/role-count` | Show how many users have a role | None |

### ℹ️ Information Commands
| Command | Description | Required Permission |
|---------|-------------|---------------------|
| `/userinfo` | Get detailed user information & mod history | Moderate Members |
| `/userpicture` | Get a user's profile picture | Send Messages |
| `/userbanner` | Get a user's nitro banner | Send Messages |
| `/serverinfo` | Display detailed server statistics | None |
| `/ping` | Check bot latency | None |

---

## ✅ Completed Commands (27 Total)

### Owner Commands (4)
- [x] `/killswitch` - Emergency bot shutdown with "offline" status
- [x] `/restart-bot` - Restart from emergency shutdown
- [x] `/owner-sleep` - Toggle sleep status page
- [x] `/updatemode` - Toggle update mode status page

### Moderation Commands (6)
- [x] `/kick` - Kick a member from the server
- [x] `/ban` - Ban a member from the server
- [x] `/unban` - Unban a user from the server
- [x] `/mute` - Timeout a member
- [x] `/unmute` - Remove timeout from a member
- [x] `/nickname` - Change a member's nickname

### Voice Moderation (5)
- [x] `/dc` - Disconnect a user from voice
- [x] `/sdeaf` - Server deafen a user in voice
- [x] `/smute` - Server mute a user in voice
- [x] `/smuteno` - Server unmute a user in voice
- [x] `/sdeafno` - Server undeafen a user in voice

### Message Management (1)
- [x] `/purge` - Mass delete messages

### Server Management (2)
- [x] `/lockdown` - Lock down the entire server
- [x] `/unlockserver` - Unlock all channels after lockdown

### Role Management (2)
- [x] `/addrole` - Give a role to a user
- [x] `/role-count` - Show how many users have a specific role

### Information Commands (7)
- [x] `/userpicture` - Get a user's profile picture
- [x] `/userbanner` - Get a user's nitro banner
- [x] `/userinfo` - Get detailed information about a user (includes mod history)
- [x] `/serverinfo` - Display detailed server information
- [x] `/ping` - Check bot latency

---

## 🚧 Work In Progress

### Information & Utility
- [ ] `membercount` - Display server member statistics
- [ ] `botinfo` - Display bot statistics and information

### Moderation Tracking
- [ ] `modnote` - Add a note about a user (visible only to mods)
- [ ] `warn` - Issue a warning to a user
- [ ] `warnings` - View warnings for a specific user
- [ ] `clearwarns` - Clear all warnings for a user
- [ ] `case` - View details of a specific moderation case
- [ ] `reason` - Add/edit reason for a moderation action

---

## 📋 Planned Commands

### Role Management
- [ ] `removerole` - Remove a role from a user
- [ ] `createrole` - Create a new role with specified permissions
- [ ] `deleterole` - Delete a role
- [ ] `roleinfo` - Display information about a role
- [ ] `rolemembers` - List all members with a specific role

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
- [ ] `roleinfo` - Get role information
- [ ] `commandinfo` - Get command permissions and information 

### Advanced Features
- [ ] `setlogchannel` - Set a channel for mod logs
- [ ] `togglelog` - Enable/disable specific log events
- [ ] `automod` - Toggle automod features (anti-spam, anti-caps, etc.)

---

## 🎨 Key Features

### Status Page
- **Endpoint**: `http://your-bot-url/` or `http://your-bot-url/health`
- **Real-time Status**: Shows current bot state with beautiful underwater theme
- **Multiple States**: Online, Offline (Emergency), Sleeping, Updating
- **Animated Effects**: Swimming fish, bubbles, seaweed, water movement

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
- **Completed:** 27 commands
- **In Progress:** 8 commands
- **Planned:** 30 commands
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
```

### Status Page Access
Once the bot is running, access the status page at:
- `http://localhost:10000/` (local development)
- `http://your-deployment-url/` (production)

---

## 🔄 Recent Updates

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

---

## 🤝 Contributing

This is a personal project by SorynTech. If you have suggestions or find bugs, feel free to reach out!

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