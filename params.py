import os
import discord
from discord.ext import commands
from bot_config import *

INITIAL_CHANNEL = int(os.environ['DISCORD_CHANNEL_ID'])
INITIAL_TEXT = "@everyone"
INITIAL_FLAG = True

channel_id = INITIAL_CHANNEL
notitext = INITIAL_TEXT
changeflag = INITIAL_FLAG
e_time = {}
channelonoff = {}
