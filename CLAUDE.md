# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**thuuwa_tuuchi_bot** is a Discord bot that monitors voice channel activity and sends notifications when users start or end calls. Written in Python using discord.py v2.3.2, designed to run in Docker containers with Cloudflare D1 for persistence.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly (requires environment variables)
python app.py

# Run with Docker Compose
docker-compose up --build
```

## Required Environment Variables

See `.env.default` for template. All variables are required:

**Discord:**
- `DISCORD_BOT_TOKEN` - Bot authentication token
- `DISCORD_APPLICATION_ID` - Application ID
- `DISCORD_GUILD_ID` - Guild (server) ID

**Cloudflare D1:**
- `D1_ACCOUNT_ID` - Cloudflare account ID
- `D1_DATABASE_ID` - D1 database ID
- `D1_API_TOKEN` - D1 API token with write access

**Optional:**
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO

## Architecture

### Core Components

**app.py** - Main bot client (`MyClient` extends `discord.Client`)
- `on_ready()` - Adds new voice channels to DB (default: notifications ON)
- `on_voice_state_update()` → `start_call()` / `end_call()` - Voice event handlers
- All settings read from D1 on every call (no in-memory caching)

**mycommands.py** - Slash commands under `/callnotion` group
- `set` - Set notification channel (saves to DB)
- `textchange`, `changenotificationmode`, `offchannel`, `reset`, `getnotiontext`, `offlist`
- All commands read/write directly to D1

**params.py** - Only contains `e_time` dict for tracking call start times (in-memory only)

**db_utils.py** - Cloudflare D1 database operations via REST API
- Tables: `notitext`, `is_target_channel`, `bot_settings`
- `bot_settings` stores `channel_id` and `is_call_end_notification_enabled` as key-value pairs

### State Management

- **All settings are read from D1 on every operation** (no caching)
- `e_time` (call start times) is the only in-memory state (lost on restart)
- Initial setup: Use `/callnotion set` to configure notification channel
- New voice channels are automatically added to DB with notifications enabled

### Call Detection Logic

**Start Call**: Channel must have exactly 1 member (the joiner), be enabled in `is_target_channel`, and user must have moved from a different channel.

**End Call**: Channel must have 0 members, `is_call_end_notification_enabled` must be true, and channel must be in `is_target_channel`.

### Deployment

Docker multi-stage build with CI/CD via GitHub Actions:
- Builds on push to `main` branch
- Multi-arch (amd64, arm64)
- Published to `ghcr.io/102ch/thuuwa-tuuchi-bot`
