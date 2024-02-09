import os
import discord
from discord.ext import commands
from bot_config import *

initial_channel = int(os.environ['DISCORD_CHANNEL_ID'])
initial_text = "@everyone"
initial_flag = True

channel_id = initial_channel
notitext = initial_text
changeflag = initial_flag
e_time = {}
channelonoff = {}
