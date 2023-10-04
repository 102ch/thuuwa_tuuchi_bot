import discord
from discord.ext import commands
from discord import Embed, Interaction, ui
import asyncio
import datetime
import pytz
import os
client = discord.Client(intents=discord.Intents.all())

TOKEN= os.environ['DISCORD_BOT_TOKEN']
application_id= os.environ['DISCORD_APPLICATION_ID']
guild_id =

initial_channel=int(os.environ['DISCORD_CHANNEL_ID'])
initial_text="@everyone"
initial_flag=True

channel_id = initial_channel
notitext = initial_text
changeflag = initial_flag
e_time={}
bot = commands.Bot(
    command_prefix="/",
    intents=discord.Intents.all(),
    application_id=application_id
)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()   
    guild = bot.get_guild(guild_id)
    for voicechannel in guild.voice_channels:
        channelonoff[voicechannel.id] = True
    print('connected')

@bot.event
async def on_voice_state_update(member: discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    if before.channel and len(before.channel.members)==0 and changeflag and channelonoff[before.channel.id]:
        if not member.status == discord.Status.idle:
            channel = bot.get_channel(channel_id)
            embed=discord.Embed(title="通話終了", color=0x6a5acd)
            embed.add_field(name="チャンネル", value=before.channel.name, inline=False)
            embed.add_field(name="通話時間", value=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))-e_time[before.channel.id], inline=False)
            e_time[before.channel.id]=0
            await channel.send(embed=embed)
    if after.channel and len(after.channel.members)==1 and channelonoff[after.channel.id]:
        print("voice state update2")
        e_time[after.channel.id]=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        if not member.status == discord.Status.idle:
            print(channel_id)
            try:
                print(channel_id)
                channel = bot.get_channel(channel_id)
                embed=discord.Embed(title="通話開始", color=0xffb6c1)
                embed.add_field(name="チャンネル", value=after.channel.name, inline=False)
                embed.add_field(name="始めた人", value=member.display_name, inline=False)
                embed.add_field(name="始めた時刻", value=datetime.datetime.now(pytz.timezone('Asia/Tokyo')), inline=False)
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(content=notitext, embed=embed)
            except Exception as e:
                print(e)

@tree.command(name="set", description="通知お知らせ君がこのチャンネルに降臨するよ！")
async def set(interaction: Interaction):
    global channel_id
    channel_id = interaction.channel.id
    await interaction.response.send_message("変更しました！")

class mode(ui.Button):
    def __init__(self, label, change):
        super().__init__(label=label)
        self.label=label
        self.change=change
    
    async def callback(self, interaction:discord.Interaction):
        global changeflag
        changeflag=self.change
        await interaction.response.edit_message(content=f'{self.label}に変更します', view=None)

@tree.command(name="changenotificationmode", description="終了時に通知をするかを変えます")
async def changenotificationmode(interaction:Interaction):
    view=ui.View()
    view.add_item(mode("終了時にも通知をする", True))
    view.add_item(mode("終了時には通知をしない", False))
    await interaction.response.send_message("選択してください", view=view)


@tree.command(name="textchange", description="通知時のテキストを変更します")
async def textchange(interaction:Interaction, newtext:str):
    global notitext
    notitext=newtext
    await interaction.response.send_message(content=f"「{notitext}」に変更します!")
class resetbutton(ui.Button):
    def __init__(self, label, initial):
        super().__init__(label=label)
        self.label=label
        self.initial=initial
    
    async def callback(self, interaction:discord.Interaction):
        global channel_id, changeflag, notitext
        if self.initial == initial_channel:
            channel_id = initial_channel
            resetmessage = bot.get_channel(initial_channel).name
        elif self.initial == initial_flag:
            changeflag = initial_flag
            resetmessage = "終了時にも通知を行う"
        elif self.initial == initial_text:
            notitext=initial_text
            resetmessage = initial_text
        elif self.initial == "allreset":
            channel_id = initial_channel
            changeflag = initial_flag
            notitext = initial_text
            resetmessage = self.initial
            await interaction.response.edit_message(content=f'{resetmessage}', view=None)
            return
        await interaction.response.edit_message(content=f'{resetmessage}に変更します', view=None)

@tree.command(name="reset", description="三つの変更可能項目についてリセットできます")
async def reset(interaction:Interaction):
    view=ui.View()
    view.add_item(resetbutton("送信チャンネル", initial_channel))
    view.add_item(resetbutton("終了時通知", initial_flag))
    view.add_item(resetbutton("通知時テキスト", initial_text))
    view.add_item(resetbutton("全て", "allreset"))
    await interaction.response.send_message(content="リセットする項目について選んでください", view=view)

class onoffbutton(ui.Button):
    def __init__(self, channelname,channelid, onoff):
        super().__init__(label=channelname, style=discord.ButtonStyle.primary if onoff else discord.ButtonStyle.secondary) #, style="Destructive" if onoff else "Secondary"
        self.channelname=channelname
        self.chnanelid=channelid
        self.onoff = onoff

    async def callback(self, interaction:discord.Interaction):
        global channelonoff
        channelonoff[self.chnanelid] = False if channelonoff[self.chnanelid] else True
        await interaction.response.edit_message(content=f'{self.channelname}を{"オン" if channelonoff[self.chnanelid] else "オフ"}に切り替えました', view=None)

class chancel_button(ui.Button):
    def __init__(self):
        super().__init__(label="中止",style=discord.ButtonStyle.red)

    async def callback(self, interaction:discord.Interaction):
        await interaction.response.edit_message(content="変更しません", view=None)

@tree.command(name="offchannel", description="オフにするチャンネルを選べます")
async def offchannel(interaction:Interaction):
    view=ui.View()
    guild = bot.get_guild(guild_id)
    for voicechannel in guild.voice_channels:
        view.add_item(onoffbutton(voicechannel.name,voicechannel.id, channelonoff[voicechannel.id]))
    view.add_item(chancel_button())

    await interaction.response.send_message(content="オンオフを切り替えられます。(青がオン)", view=view) #ephemeral = True

@tree.command(name="offlist", description="オフにするチャンネルを選べます")
async def offlist(interaction:Interaction):
    embed=discord.Embed(title="チャンネルのオンオフです", color=0x00E5FF)
    guild = bot.get_guild(guild_id)
    for voicechannel in guild.voice_channels:
        embed.add_field(name=voicechannel.name, value=":o:" if channelonoff[voicechannel.id] else ":x:", inline=False)
    await interaction.response.send_message(embed=embed)


async def main():
    # start the client
    async with bot:

        await bot.start(TOKEN)

asyncio.run(main())
