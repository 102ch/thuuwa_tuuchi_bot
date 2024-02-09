from discord import app_commands, Interaction, ui
import discord
from params import *

class CallNotification(app_commands.Group):
    def __init__(self, name: str):
        super().__init__(name=name)
    
    @app_commands.command(name="set", description="通知お知らせ君がこのチャンネルに降臨するよ！")
    async def set(self, interaction: Interaction):
        global channel_id
        channel_id = interaction.channel.id
        await interaction.response.send_message("変更しました！")

    class mode(ui.Button):
        def __init__(self, label, change):
            super().__init__(label=label)
            self.label = label
            self.change = change

        async def callback(self, interaction: discord.Interaction):
            global changeflag
            changeflag = self.change
            await interaction.response.edit_message(content=f'{self.label}に変更します', view=None)

    @app_commands.command(name="changenotificationmode", description="終了時に通知をするかを変えます")
    async def changenotificationmode(self, interaction: Interaction):
        view = ui.View()
        view.add_item(self.mode("終了時にも通知をする", True))
        view.add_item(self.mode("終了時には通知をしない", False))
        await interaction.response.send_message("選択してください", view=view)

    @app_commands.command(name="textchange", description="通知時のテキストを変更します")
    async def textchange(self, interaction: Interaction, newtext: str):
        global notitext
        notitext = newtext
        await interaction.response.send_message(content=f"「{notitext}」に変更します!")

    class resetbutton(ui.Button):
        def __init__(self, label, initial):
            super().__init__(label=label)
            self.label = label
            self.initial = initial

        async def callback(self, interaction: discord.Interaction):
            global channel_id, changeflag, notitext
            if self.initial == initial_channel:
                channel_id = initial_channel
                resetmessage = bot.get_channel(initial_channel).name
            elif self.initial == initial_flag:
                changeflag = initial_flag
                resetmessage = "終了時にも通知を行う"
            elif self.initial == initial_text:
                notitext = initial_text
                resetmessage = initial_text
            elif self.initial == "allreset":
                channel_id = initial_channel
                changeflag = initial_flag
                notitext = initial_text
                resetmessage = self.initial
                await interaction.response.edit_message(content=f'{resetmessage}', view=None)
                return
            await interaction.response.edit_message(content=f'{resetmessage}に変更します', view=None)

    @app_commands.command(name="reset", description="三つの変更可能項目についてリセットできます")
    async def reset(self, interaction: Interaction):
        view = ui.View()
        view.add_item(self.resetbutton("送信チャンネル", initial_channel))
        view.add_item(self.resetbutton("終了時通知", initial_flag))
        view.add_item(self.resetbutton("通知時テキスト", initial_text))
        view.add_item(self.resetbutton("全て", "allreset"))
        await interaction.response.send_message(content="リセットする項目について選んでください", view=view)


    class onoffbutton(ui.Button):
        def __init__(self, channelname, channelid, onoff):
            super().__init__(label=channelname,
                            style=discord.ButtonStyle.primary if onoff else discord.ButtonStyle.secondary)
            self.channelname = channelname
            self.chnanelid = channelid
            self.onoff = onoff

        async def callback(self, interaction: discord.Interaction):
            global channelonoff
            channelonoff[self.chnanelid] = False if channelonoff[self.chnanelid] else True
            await interaction.response.edit_message(content=f'{self.channelname}を{"オン" if channelonoff[self.chnanelid] else "オフ"}に切り替えました', view=None)


    class chancel_button(ui.Button):
        def __init__(self):
            super().__init__(label="中止", style=discord.ButtonStyle.red)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(content="変更しません", view=None)


    @app_commands.command(name="offchannel", description="オフにするチャンネルを選べます")
    async def offchannel(self, interaction: Interaction):
        view = ui.View()
        guild = bot.get_guild(GUILD_ID)
        for voicechannel in guild.voice_channels:
            view.add_item(self.onoffbutton(voicechannel.name,
                        voicechannel.id, channelonoff[voicechannel.id]))
        view.add_item(self.chancel_button())
        await interaction.response.send_message(content="オンオフを切り替えられます。(青がオン)", view=view)


    @app_commands.command(name="offlist", description="オフにするチャンネルを選べます")
    async def offlist(self, interaction: Interaction):
        embed = discord.Embed(title="チャンネルのオンオフです", color=0x00E5FF)
        guild = bot.get_guild(GUILD_ID)
        for voicechannel in guild.voice_channels:
            embed.add_field(name=voicechannel.name,
                            value=":o:" if channelonoff[voicechannel.id] else ":x:", inline=False)
        await interaction.response.send_message(embed=embed)