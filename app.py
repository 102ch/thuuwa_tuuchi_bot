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
            if member.status == discord.Status.idle: return
            print(channel_id)
            try:
                print(channel_id)
                channel = self.get_channel(channel_id)
                embed = discord.Embed(title="通話開始", color=0xffb6c1)
                embed.add_field(name="チャンネル", value=after.channel.name, inline=False)
                embed.add_field(name="始めた人", value=member.display_name, inline=False)
                current_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
                e_time[after.channel.id] = current_time
                current_time_str = current_time.strftime('%Y-%m-%d %X')
                embed.add_field(name="始めた時刻", value=current_time_str, inline=False)
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(content=params.notitext, embed=embed)
            except Exception as e:
                print(e)
    
    def format_timedelta(self, timedelta):
        total_sec = timedelta.total_seconds()
        # hours
        hours = total_sec // 3600 
        # remaining seconds
        remain = total_sec - (hours * 3600)
        # minutes
        minutes = remain // 60
        # remaining seconds
        seconds = remain - (minutes * 60)
        # total time
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    
    def get_elapsed_time(self, start_time):
        current_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        elapsed_time: datetime.timedelta = current_time - start_time
        elapsed_time_str = self.format_timedelta(elapsed_time)
        return elapsed_time_str
    
    async def end_call(self, before, after, member):
        # この関数はボイスチャンネルの状態が変化したときに呼び出される
        # beforeは変化前の状態、afterは変化後の状態

        # 通話終了通知をしない設定になっているなら何もしない
        if not is_call_end_notification_enabled: return

        # 変化前のチャンネルが存在しないなら通話終了ではない
        if not before.channel: return

        # 通知対象のチャンネルではないなら何もしない
        if not channelonoff.get(before.channel.id, False): return
        
        # 変化前のチャンネルの現在のメンバー数が0なら通話終了
        if len(before.channel.members) == 0:
            channel = self.get_channel(channel_id)
            embed = discord.Embed(title="通話終了", color=0x6a5acd)
            embed.add_field(name="チャンネル", value=before.channel.name, inline=False)
            elapsed_time_str: str = self.get_elapsed_time(e_time[before.channel.id])
            embed.add_field(name="通話時間", value=elapsed_time_str, inline=False)
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
