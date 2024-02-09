import discord
from discord.ext import commands
from discord import Embed, Interaction, ui
import asyncio
import datetime
import pytz
import os
from modules.commands import CallNotification
from bot_config import *
from discord.app_commands import CommandTree

initial_channel = int(os.environ['DISCORD_CHANNEL_ID'])
initial_text = "@everyone"
initial_flag = True

channel_id = initial_channel
notitext = initial_text
changeflag = initial_flag
e_time = {}
channelonoff = {}
bot = commands.Bot(
    command_prefix="/",
    intents=discord.Intents.all(),
    application_id=APPLICATION_ID
)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents,) -> None:
        super().__init__(intents=intents)
        self.tree = bot.tree
        self.tree.add_command(CallNotification('callnoification'))
    
    async def on_ready(self):
        await self.tree.sync()
        guild = bot.get_guild(GUILD_ID)
        for voicechannel in guild.voice_channels:
            channelonoff[voicechannel.id] = True
        print('connected')

    async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel and len(before.channel.members) == 0 and changeflag and channelonoff[before.channel.id]:
            if not member.status == discord.Status.idle:
                channel = bot.get_channel(channel_id)
                embed = discord.Embed(title="通話終了", color=0x6a5acd)
                embed.add_field(
                    name="チャンネル", value=before.channel.name, inline=False)
                embed.add_field(name="通話時間", value=datetime.datetime.now(
                    pytz.timezone('Asia/Tokyo'))-e_time[before.channel.id], inline=False)
                e_time[before.channel.id] = 0
                await channel.send(embed=embed)
        if after.channel and len(after.channel.members) == 1 and channelonoff[after.channel.id]:
            print("voice state update2")
            e_time[after.channel.id] = datetime.datetime.now(
                pytz.timezone('Asia/Tokyo'))
            if not member.status == discord.Status.idle:
                print(channel_id)
                try:
                    print(channel_id)
                    channel = bot.get_channel(channel_id)
                    embed = discord.Embed(title="通話開始", color=0xffb6c1)
                    embed.add_field(
                        name="チャンネル", value=after.channel.name, inline=False)
                    embed.add_field(
                        name="始めた人", value=member.display_name, inline=False)
                    embed.add_field(name="始めた時刻", value=datetime.datetime.now(
                        pytz.timezone('Asia/Tokyo')), inline=False)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(content=notitext, embed=embed)
                except Exception as e:
                    print(e)

def main():
    # start the client
    client = MyClient(intents=INTENTS)
    client.run(TOKEN)

if __name__ == "__main__":
    main()
