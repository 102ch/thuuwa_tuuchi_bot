import os
from db_utils import load_notitext, load_is_target_channels

INITIAL_CHANNEL = int(os.environ['DISCORD_CHANNEL_ID'])
INITIAL_TEXT = "@everyone"
INITIAL_FLAG = True

channel_id = INITIAL_CHANNEL
is_call_end_notification_enabled = INITIAL_FLAG
e_time = {}
try:
    notitext = load_notitext()  # データベースから読み込み
    is_target_channel = load_is_target_channels()  # データベースから読み込み
except:
    notitext = INITIAL_TEXT
    is_target_channel = {}