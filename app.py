import discord
from discord.app_commands import CommandTree
import datetime
import pytz
from mycommands import CallNotification
from bot_config import *
from params import *
import params
import db_utils


class MyClient(discord.Client):
    def __init__(
        self,
        *,
        intents: discord.Intents,
    ) -> None:
        super().__init__(intents=intents)
        self.tree = CommandTree(self)
        self.tree.add_command(CallNotification("callnotion", client=self))
        db_utils.init_db()

    async def on_ready(self):
        guild = self.get_guild(GUILD_ID)
        print("connected")
        # データベースから現在のターゲットチャンネル設定を読み込む
        current_channels = db_utils.load_is_target_channels()

        # すべてのボイスチャンネルをチェック
        for channel in guild.voice_channels:
            print(channel.name)
            print(channel.id)
            # チャンネルがデータベースに存在しない場合は、Trueとして追加
            if channel.id not in current_channels:
                is_target_channel[channel.id] = True
                db_utils.save_is_target_channel(channel.id, True)
            else:
                # 既存の設定を反映
                is_target_channel[channel.id] = current_channels[channel.id]

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def start_call(self, before, after, member):
        # 変化後のチャンネルが存在しないなら通話開始ではない
        if not after.channel:
            print("after channel is None")
            return

        # 通知対象のチャンネルではないなら何もしない
        if not is_target_channel.get(after.channel.id, False):
            print("not target channel")
            return

        # チャンネルを移動していないなら何もしない
        if before.channel == after.channel:
            print("not moved")
            return

        # チャンネルに人がいないなら通話開始ではない
        if len(after.channel.members) == 0:
            print("no members")
            return

        # チャンネルの人数が2人以上なら通話開始ではない
        if len(after.channel.members) > 1:
            print("more than 2 members")
            return

        print("voice state update2")
        print(params.channel_id)
        try:
            print(params.channel_id)
            channel = self.get_channel(params.channel_id)
            embed = discord.Embed(title="通話開始", color=0xFFB6C1)
            embed.add_field(name="チャンネル", value=after.channel.name, inline=False)
            embed.add_field(name="始めた人", value=member.display_name, inline=False)
            current_time = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
            e_time[after.channel.id] = current_time
            current_time_str = current_time.strftime("%Y-%m-%d %X")
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
        return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

    def get_elapsed_time(self, start_time):
        current_time = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
        elapsed_time: datetime.timedelta = current_time - start_time
        elapsed_time_str = self.format_timedelta(elapsed_time)
        return elapsed_time_str

    async def end_call(self, before, after, member):
        # この関数はボイスチャンネルの状態が変化したときに呼び出される
        # beforeは変化前の状態、afterは変化後の状態

        # 通話終了通知をしない設定になっているなら何もしない
        if not is_call_end_notification_enabled:
            print("通話終了通知をしない設定になっています")
            return

        # 変化前のチャンネルが存在しないなら通話終了ではない
        if not before.channel:
            print("before channel is None")
            return

        # 通知対象のチャンネルではないなら何もしない
        if not is_target_channel.get(before.channel.id, False):
            print("not target channel")
            return

        # 変化前のチャンネルの現在のメンバー数が0なら通話終了
        if len(before.channel.members) == 0:
            channel = self.get_channel(params.channel_id)
            embed = discord.Embed(title="通話終了", color=0x6A5ACD)
            embed.add_field(name="チャンネル", value=before.channel.name, inline=False)
            elapsed_time_str: str = self.get_elapsed_time(e_time[before.channel.id])
            embed.add_field(name="通話時間", value=elapsed_time_str, inline=False)
            e_time[before.channel.id] = 0
            await channel.send(embed=embed)
            return

    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        print("voice state update")
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
