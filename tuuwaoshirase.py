import discord
from discord.ext import commands
from discord import Embed, Interaction, ui
import asyncio
import datetime
import pytz
client = discord.Client(intents=discord.Intents.all())
TOKEN=""
application_id=""
channel_id = 841990187047583764
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
    print('connected')

@bot.event
async def on_voice_state_update(member: discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    if after.channel and not before.channel and len(after.channel.members)==1:
        e_time[after.channel.id]=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        if not member.status == discord.Status.idle:
            channel = bot.get_channel(channel_id)
            embed=discord.Embed(title="通話開始", color=0xffb6c1)
            embed.add_field(name="チャンネル", value=after.channel.name, inline=False)
            embed.add_field(name="始めた人", value=member.display_name, inline=False)
            embed.add_field(name="始めた時刻", value=datetime.datetime.now(pytz.timezone('Asia/Tokyo')), inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(content="@everyone", embed=embed)
    
    if before.channel and not after.channel and len(before.channel.members)==0:
        if not member.status == discord.Status.idle:
            channel = bot.get_channel(channel_id)
            embed=discord.Embed(title="通話終了", color=0x6a5acd)
            embed.add_field(name="チャンネル", value=before.channel.name, inline=False)
            embed.add_field(name="通話時間", value=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))-e_time[before.channel.id], inline=False)
            e_time[before.channel.id]=0
            await channel.send(embed=embed)

@tree.command(name="set", description="匿名ちゃんがこのチャンネルに降臨するよ！")
async def set(interaction: Interaction):
    global channel_id
    channel_id = interaction.channel.id
    await interaction.response.send_message("変更しました！")

async def main():
    # start the client
    async with bot:

        await bot.start(TOKEN)

asyncio.run(main())
