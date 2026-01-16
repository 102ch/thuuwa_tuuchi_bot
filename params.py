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
    print(f"[DB] notitext loaded: {notitext}")

    is_target_channel = load_is_target_channels()  # データベースから読み込み
    print(f"[DB] is_target_channel loaded: {len(is_target_channel)} channels")

    # channel_idをデータベースから読み込み、なければ初期値を使用
    loaded_channel_id = load_channel_id()
    channel_id = loaded_channel_id if loaded_channel_id is not None else INITIAL_CHANNEL
    print(f"[DB] channel_id loaded: {channel_id} (from DB: {loaded_channel_id is not None})")

    # is_call_end_notification_enabledをデータベースから読み込み、なければ初期値を使用
    loaded_end_notification = load_call_end_notification_enabled()
    is_call_end_notification_enabled = loaded_end_notification if loaded_end_notification is not None else INITIAL_FLAG
    print(f"[DB] is_call_end_notification_enabled loaded: {is_call_end_notification_enabled} (from DB: {loaded_end_notification is not None})")
except Exception as e:
    print(f"[DB] ERROR: Failed to load from database: {e}")
    notitext = INITIAL_TEXT
    is_target_channel = {}
    channel_id = INITIAL_CHANNEL
    is_call_end_notification_enabled = INITIAL_FLAG