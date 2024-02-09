import os
import discord

TOKEN = os.environ['DISCORD_BOT_TOKEN']
APPLICATION_ID = int(os.environ['DISCORD_APPLICATION_ID'])
GUILD_ID = int(os.environ['DISCORD_GUILD_ID'])
INTENTS = discord.Intents.all()