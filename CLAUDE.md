# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**thuuwa_tuuchi_bot** is a Discord bot that monitors voice channel activity and sends notifications when users start or end calls. The bot is written in Python using discord.py v2.3.2 and is designed to run in Docker containers.

## Development Commands

### Running the Bot Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run directly (requires environment variables)
python app.py

# Run with Docker Compose
docker-compose up --build
```

### Required Environment Variables
The following environment variables must be set (see `.env.default` for template):
- `DISCORD_BOT_TOKEN` - Discord bot authentication token
- `DISCORD_APPLICATION_ID` - Discord application ID
- `DISCORD_CHANNEL_ID` - Default channel ID for notifications
- `DISCORD_GUILD_ID` - Discord guild (server) ID

## Architecture

### Core Components

**app.py** - Main bot client and event handlers
- `MyClient` class extends `discord.Client` with custom voice state monitoring
- `on_ready()` - Initializes database and syncs voice channel settings on bot startup
- `on_voice_state_update()` - Monitors voice channel join/leave events
- `start_call()` - Detects when a user starts a new call (first person joins empty channel)
- `end_call()` - Detects when a call ends (last person leaves channel)

**mycommands.py** - Discord slash commands (`/callnotion` command group)
- `set` - Configure notification target channel
- `textchange` - Change notification message text
- `changenotificationmode` - Toggle end-call notifications on/off
- `offchannel` - Enable/disable notifications per voice channel (interactive UI)
- `offlist` - View on/off status of all voice channels
- `reset` - Reset configuration to defaults
- `getnotiontext` - View current notification text

**bot_config.py** - Configuration loader
- Loads required environment variables for Discord API
- Defines bot intents (requires `discord.Intents.all()`)

**params.py** - Runtime state management
- Loads persistent settings from database on startup
- Stores in-memory state: `channel_id`, `notitext`, `is_target_channel`, `e_time`
- Falls back to initial values if database load fails

**db_utils.py** - SQLite database operations
- Database path: `db/bot_data.db`
- Tables:
  - `notitext` - Stores notification message text
  - `is_target_channel` - Stores per-channel notification enable/disable status
- `init_db()` - Creates tables if they don't exist
- CRUD functions for notification text and channel targeting settings

### State Flow

1. Bot starts → `init_db()` creates database schema
2. `params.py` loads persistent settings from database
3. `on_ready()` syncs voice channels with database (adds new channels as enabled by default)
4. Voice state changes trigger `on_voice_state_update()` → `start_call()` or `end_call()`
5. Slash commands update both in-memory state (`params.py`) and database (`db_utils.py`)

### Call Detection Logic

**Start Call Detection** (app.py:44-86):
- User must move to a different channel (not already in it)
- Target channel must be enabled for notifications (`is_target_channel[channel_id] == True`)
- Channel must have exactly 1 member (the person who just joined)
- Sends embed with channel name, starter's name, timestamp, and user avatar

**End Call Detection** (app.py:107-136):
- Only runs if `is_call_end_notification_enabled == True`
- User must leave from a tracked channel
- Channel must now have 0 members
- Sends embed with channel name and elapsed call duration (formatted as HH:MM:SS)

### Deployment

The bot is containerized with multi-stage Docker build:
- CI/CD via GitHub Actions (`.github/workflows/image-build.yml`)
- Builds on push to `main` branch
- Multi-architecture support (amd64, arm64)
- Published to GitHub Container Registry: `ghcr.io/102ch/thuuwa-tuuchi-bot`
