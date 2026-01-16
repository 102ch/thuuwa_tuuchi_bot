import os
from db_utils import (
    load_notitext,
    load_is_target_channels,
    load_channel_id,
    load_call_end_notification_enabled,
)

INITIAL_CHANNEL = int(os.environ['DISCORD_CHANNEL_ID'])
INITIAL_TEXT = "@everyone"
INITIAL_FLAG = True

e_time = {}
try:
    notitext = load_notitext()  # データベースから読み込み
    is_target_channel = load_is_target_channels()  # データベースから読み込み
    # channel_idをデータベースから読み込み、なければ初期値を使用
    loaded_channel_id = load_channel_id()
    channel_id = loaded_channel_id if loaded_channel_id is not None else INITIAL_CHANNEL
    # is_call_end_notification_enabledをデータベースから読み込み、なければ初期値を使用
    loaded_end_notification = load_call_end_notification_enabled()
    is_call_end_notification_enabled = loaded_end_notification if loaded_end_notification is not None else INITIAL_FLAG
except:
    notitext = INITIAL_TEXT
    is_target_channel = {}
    channel_id = INITIAL_CHANNEL
    is_call_end_notification_enabled = INITIAL_FLAG