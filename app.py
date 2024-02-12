import discord
from discord.app_commands import CommandTree
import datetime
import pytz
from mycommands import CallNotification
from bot_config import *
from params import *
import params

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents,) -> None:
        super().__init__(intents=intents)
        self.tree = CommandTree(self)
        self.tree.add_command(CallNotification('callnotion', client=self))
    
    async def on_ready(self):
        guild = self.get_guild(GUILD_ID)
        for voicechannel in guild.voice_channels:
            channelonoff[voicechannel.id] = True
        print('connected')
    
    async def setup_hook(self) -> None:
        await self.tree.sync()
        
    def is_call_start(self, before, after, member):
        # voice state update後のチャンネルが存在しないなら通話開始ではない
        if after.channel == None: return False

        # 通話開始かどうかの判断
        is_different_voice_channel = before.channel != after.channel
        member_count_after = len(after.channel.members)
        is_start_call = is_different_voice_channel and member_count_after == 1
        
        return is_start_call
    
    async def start_call(self, before, after, member):
        if after.channel == None: return
        if channelonoff[after.channel.id] == False: return
        
        if self.is_call_start(before, after, member):
            print("voice state update2")
            current_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
            e_time[after.channel.id] = current_time
            if member.status == discord.Status.idle: return
            print(channel_id)
            try:
                print(channel_id)
                channel = self.get_channel(channel_id)
                embed = discord.Embed(title="通話開始", color=0xffb6c1)
                embed.add_field(name="チャンネル", value=after.channel.name, inline=False)
                embed.add_field(name="始めた人", value=member.display_name, inline=False)
                print(current_time, type(current_time))
                embed.add_field(name="始めた時刻", value=current_time, inline=False)
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(content=params.notitext, embed=embed)
            except Exception as e:
                print(e)

    async def end_call(self, before, after, member):
        if before.channel == None: return
        if channelonoff[before.channel.id] == False: return
        
        if before.channel and len(before.channel.members) == 0 and is_call_end_notification_enabled:
            if member.status == discord.Status.idle: return
            channel = self.get_channel(channel_id)
            embed = discord.Embed(title="通話終了", color=0x6a5acd)
            embed.add_field(name="チャンネル", value=before.channel.name, inline=False)
            current_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
            elapsed_time = current_time - e_time[before.channel.id]
            print(elapsed_time, type(elapsed_time))
            embed.add_field(name="通話時間", value=elapsed_time, inline=False)
            e_time[before.channel.id] = 0
            await channel.send(embed=embed)
            return
        
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # 通話終了通知
        await self.end_call(before, after, member)
        # 通話開始通知
        await self.start_call(before, after, member)
        

def main():
    # start the client
    client = MyClient(intents=INTENTS)
    client.run(TOKEN)

if __name__ == "__main__":
    main()
