import discord
from discord import app_commands, Interaction, ui
from bot_config import *
from db_utils import (
    save_notitext, save_is_target_channel, save_channel_id, save_call_end_notification_enabled,
    load_notitext, load_is_target_channels
)
from params import e_time  # e_timeのみ使用（通話時間計測用）

# デフォルト値（リセット用）
DEFAULT_TEXT = "@everyone"
DEFAULT_END_NOTIFICATION = True


class CallNotification(app_commands.Group):
    def __init__(self, name: str, client: discord.Client):
        super().__init__(name=name)
        self.client = client

    @app_commands.command(
        name="set", description="通知お知らせ君がこのチャンネルに降臨するよ！"
    )
    async def set(self, interaction: Interaction):
        save_channel_id(interaction.channel.id)  # データベースに保存
        await interaction.response.send_message("変更しました！")

    class CallEndNotificationChangeButton(ui.Button):
        def __init__(self, label, change):
            super().__init__(label=label)
            self.label = label
            self.change = change

        async def callback(self, interaction: discord.Interaction):
            save_call_end_notification_enabled(self.change)  # データベースに保存
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
        save_notitext(newtext)  # データベースに保存
        await interaction.response.send_message(
            content=f"「{newtext}」に変更します!"
        )

    class resetbutton(ui.Button):
        def __init__(self, label, reset_type, client):
            super().__init__(label=label)
            self.label = label
            self.reset_type = reset_type
            self.client = client

        async def callback(self, interaction: discord.Interaction):
            if self.reset_type == "end_notification":
                save_call_end_notification_enabled(DEFAULT_END_NOTIFICATION)  # データベースに保存
                resetmessage = "終了時にも通知を行う"
            elif self.reset_type == "notitext":
                save_notitext(DEFAULT_TEXT)  # データベースに保存
                resetmessage = DEFAULT_TEXT
            elif self.reset_type == "allreset":
                save_call_end_notification_enabled(DEFAULT_END_NOTIFICATION)  # データベースに保存
                save_notitext(DEFAULT_TEXT)  # データベースに保存
                resetmessage = "終了時通知と通知テキストをリセットしました"
                await interaction.response.edit_message(
                    content=resetmessage, view=None
                )
                return
            await interaction.response.edit_message(
                content=f"{resetmessage}に変更します", view=None
            )

    @app_commands.command(
        name="reset", description="設定をリセットできます"
    )
    async def reset(self, interaction: Interaction):
        view = ui.View()
        view.add_item(self.resetbutton("終了時通知", "end_notification", self.client))
        view.add_item(self.resetbutton("通知時テキスト", "notitext", self.client))
        view.add_item(self.resetbutton("全て", "allreset", self.client))
        await interaction.response.send_message(
            content="リセットする項目について選んでください", view=view
        )

    class OffChannelView(ui.View):
        def __init__(self, client):
            super().__init__(timeout=180)  # 3分でタイムアウト
            self.client = client
            self._build_buttons()

        def _build_buttons(self):
            self.clear_items()
            guild = self.client.get_guild(GUILD_ID)
            current_channels = load_is_target_channels()
            for voicechannel in guild.voice_channels:
                is_on = current_channels.get(voicechannel.id, True)
                button = ui.Button(
                    label=voicechannel.name,
                    style=discord.ButtonStyle.primary if is_on else discord.ButtonStyle.secondary,
                    custom_id=f"toggle_{voicechannel.id}",
                )
                button.callback = self._make_toggle_callback(voicechannel.name, voicechannel.id)
                self.add_item(button)
            cancel_button = ui.Button(label="中止", style=discord.ButtonStyle.red, custom_id="cancel")
            cancel_button.callback = self._cancel_callback
            self.add_item(cancel_button)

        def _make_toggle_callback(self, channelname, channelid):
            async def callback(interaction: discord.Interaction):
                current_channels = load_is_target_channels()
                current_value = current_channels.get(channelid, True)
                new_value = not current_value
                save_is_target_channel(channelid, new_value)
                self._build_buttons()
                await interaction.response.edit_message(
                    content=f'{channelname}を{"オン" if new_value else "オフ"}に切り替えました。(青がオン)',
                    view=self,
                )
            return callback

        async def _cancel_callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(content="変更を終了しました", view=None)

        async def on_timeout(self):
            pass  # タイムアウト時は何もしない（メッセージは残る）

    @app_commands.command(
        name="offchannel", description="オフにするチャンネルを選べます"
    )
    async def offchannel(self, interaction: Interaction):
        view = self.OffChannelView(self.client)
        await interaction.response.send_message(
            content="オンオフを切り替えられます。(青がオン)", view=view
        )

    @app_commands.command(name="offlist", description="チャンネルごとのONOFFを確認できます")
    async def offlist(self, interaction: Interaction):
        await interaction.response.defer()  # タイムアウト防止
        embed = discord.Embed(title="チャンネルのオンオフです", color=0x00E5FF)
        guild = self.client.get_guild(GUILD_ID)
        # DBから最新の状態を読み込む
        current_channels = load_is_target_channels()
        for voicechannel in guild.voice_channels:
            embed.add_field(
                name=voicechannel.name,
                value=":o:" if current_channels.get(voicechannel.id, True) else ":x:",
                inline=False,
            )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="getnotiontext", description="通知時のテキストの現在の設定値の確認用です。"
    )
    async def getnotiontext(self, interaction: Interaction):
        # DBから最新の状態を読み込む
        current_text = load_notitext()
        await interaction.response.send_message(
            content=f"現在の通知時テキストは「{current_text}」です。", silent=True
        )
