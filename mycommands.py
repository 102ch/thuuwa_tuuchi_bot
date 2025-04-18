import discord
from discord import app_commands, Interaction, ui
from params import *
from bot_config import *
import params
from db_utils import save_notitext, save_is_target_channel


class CallNotification(app_commands.Group):
    def __init__(self, name: str, client: discord.Client):
        super().__init__(name=name)
        self.client = client

    @app_commands.command(
        name="set", description="通知お知らせ君がこのチャンネルに降臨するよ！"
    )
    async def set(self, interaction: Interaction):
        global channel_id
        channel_id = interaction.channel.id
        await interaction.response.send_message("変更しました！")

    class CallEndNotificationChangeButton(ui.Button):
        def __init__(self, label, change):
            super().__init__(label=label)
            self.label = label
            self.change = change

        async def callback(self, interaction: discord.Interaction):
            global is_call_end_notification_enabled
            is_call_end_notification_enabled = self.change
            await interaction.response.edit_message(
                content=f"{self.label}に変更します", view=None
            )

    @app_commands.command(
        name="changenotificationmode", description="終了時に通知をするかを変えます"
    )
    async def changenotificationmode(self, interaction: Interaction):
        view = ui.View()
        view.add_item(
            self.CallEndNotificationChangeButton("終了時にも通知をする", True)
        )
        view.add_item(
            self.CallEndNotificationChangeButton("終了時には通知をしない", False)
        )
        await interaction.response.send_message("選択してください", view=view)

    @app_commands.command(name="textchange", description="通知時のテキストを変更します")
    async def textchange(self, interaction: Interaction, newtext: str):
        params.notitext = newtext
        save_notitext(newtext)  # データベースに保存
        await interaction.response.send_message(
            content=f"「{params.notitext}」に変更します!"
        )

    class resetbutton(ui.Button):
        def __init__(self, label, initial, client):
            super().__init__(label=label)
            self.label = label
            self.initial = initial
            self.client = client

        async def callback(self, interaction: discord.Interaction):
            global channel_id, is_call_end_notification_enabled, notitext
            if self.initial == INITIAL_CHANNEL:
                channel_id = INITIAL_CHANNEL
                resetmessage = self.client.get_channel(INITIAL_CHANNEL).name
            elif self.initial == INITIAL_FLAG:
                is_call_end_notification_enabled = INITIAL_FLAG
                resetmessage = "終了時にも通知を行う"
            elif self.initial == INITIAL_TEXT:
                notitext = INITIAL_TEXT
                resetmessage = INITIAL_TEXT
            elif self.initial == "allreset":
                channel_id = INITIAL_CHANNEL
                is_call_end_notification_enabled = INITIAL_FLAG
                notitext = INITIAL_TEXT
                resetmessage = self.initial
                await interaction.response.edit_message(
                    content=f"{resetmessage}", view=None
                )
                return
            await interaction.response.edit_message(
                content=f"{resetmessage}に変更します", view=None
            )

    @app_commands.command(
        name="reset", description="三つの変更可能項目についてリセットできます"
    )
    async def reset(self, interaction: Interaction):
        view = ui.View()
        view.add_item(self.resetbutton("送信チャンネル", INITIAL_CHANNEL, self.client))
        view.add_item(self.resetbutton("終了時通知", INITIAL_FLAG, self.client))
        view.add_item(self.resetbutton("通知時テキスト", INITIAL_TEXT, self.client))
        view.add_item(self.resetbutton("全て", "allreset", self.client))
        await interaction.response.send_message(
            content="リセットする項目について選んでください", view=view
        )

    class onoffbutton(ui.Button):
        def __init__(self, channelname, channelid, onoff):
            super().__init__(
                label=channelname,
                style=(
                    discord.ButtonStyle.primary
                    if onoff
                    else discord.ButtonStyle.secondary
                ),
            )
            self.channelname = channelname
            self.channelid = channelid
            self.onoff = onoff

        async def callback(self, interaction: discord.Interaction):
            params.is_target_channel[self.channelid] = not params.is_target_channel.get(
                self.channelid, True
            )
            save_is_target_channel(self.channelid, params.is_target_channel[self.channelid])
            await interaction.response.edit_message(
                content=f'{self.channelname}を{"オン" if params.is_target_channel.get(self.channelid, None) else "オフ"}に切り替えました',
                view=None,
            )

    class chancel_button(ui.Button):
        def __init__(self):
            super().__init__(label="中止", style=discord.ButtonStyle.red)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(content="変更しません", view=None)

    @app_commands.command(
        name="offchannel", description="オフにするチャンネルを選べます"
    )
    async def offchannel(self, interaction: Interaction):
        view = ui.View()
        guild = self.client.get_guild(GUILD_ID)
        for voicechannel in guild.voice_channels:
            view.add_item(
                self.onoffbutton(
                    voicechannel.name,
                    voicechannel.id,
                    is_target_channel.get(voicechannel.id, True),
                )
            )
        view.add_item(self.chancel_button())
        await interaction.response.send_message(
            content="オンオフを切り替えられます。(青がオン)", view=view
        )

    @app_commands.command(name="offlist", description="チャンネルごとのONOFFを確認できます")
    async def offlist(self, interaction: Interaction):
        embed = discord.Embed(title="チャンネルのオンオフです", color=0x00E5FF)
        guild = self.client.get_guild(GUILD_ID)
        for voicechannel in guild.voice_channels:
            embed.add_field(
                name=voicechannel.name,
                value=":o:" if is_target_channel.get(voicechannel.id, True) else ":x:",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="getnotiontext", description="通知時のテキストの現在の設定値の確認用です。"
    )
    async def getnotiontext(self, interaction: Interaction):
        await interaction.response.send_message(
            content=f"現在の通知時テキストは「{params.notitext}」です。", silent=True
        )
