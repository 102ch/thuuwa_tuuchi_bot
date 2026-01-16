import os
import logging
import requests
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# D1設定（環境変数から読み込み）
D1_ACCOUNT_ID = os.environ.get("D1_ACCOUNT_ID")
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID")
D1_API_TOKEN = os.environ.get("D1_API_TOKEN")

if not all([D1_ACCOUNT_ID, D1_DATABASE_ID, D1_API_TOKEN]):
    raise ValueError("Missing D1 environment variables: D1_ACCOUNT_ID, D1_DATABASE_ID, D1_API_TOKEN")

D1_API_URL = f"https://api.cloudflare.com/client/v4/accounts/{D1_ACCOUNT_ID}/d1/database/{D1_DATABASE_ID}/query"


def execute_d1_query(sql: str, params: Optional[List] = None) -> dict:
    """D1データベースでクエリを実行"""
    headers = {
        "Authorization": f"Bearer {D1_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {"sql": sql}
    if params:
        payload["params"] = params

    try:
        response = requests.post(D1_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            raise ValueError(f"D1 query failed: {data.get('errors', [])}")

        return data["result"][0] if data.get("result") else {}

    except requests.exceptions.RequestException as e:
        logger.error(f"D1 API request failed: {e}")
        raise


def init_db():
    """D1データベーススキーマを初期化"""
    execute_d1_query("""
        CREATE TABLE IF NOT EXISTS notitext (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    """)

    execute_d1_query("""
        CREATE TABLE IF NOT EXISTS is_target_channel (
            channel_id TEXT PRIMARY KEY,
            is_target BOOLEAN NOT NULL
        )
    """)

    execute_d1_query("""
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    logger.info("D1 database initialized")


def save_notitext(text: str):
    """通知テキストをD1に保存"""
    execute_d1_query("DELETE FROM notitext")
    execute_d1_query("INSERT INTO notitext (text) VALUES (?)", [text])


def load_notitext() -> str:
    """通知テキストをD1から読み込み"""
    result = execute_d1_query("SELECT text FROM notitext LIMIT 1")
    results = result.get("results", [])

    if results and len(results) > 0:
        return results[0]["text"]

    return "@everyone"


def save_is_target_channel(channel_id: int, is_target: bool):
    """チャンネル設定をD1に保存（channel_idは文字列として保存）"""
    logger.debug(f"Saving is_target_channel: channel_id={channel_id}, is_target={is_target}")
    result = execute_d1_query(
        "INSERT OR REPLACE INTO is_target_channel (channel_id, is_target) VALUES (?, ?)",
        [str(channel_id), 1 if is_target else 0]
    )
    logger.debug(f"save_is_target_channel result: {result}")


def load_is_target_channels() -> Dict[int, bool]:
    """全チャンネル設定をD1から読み込み（channel_idは文字列として保存されている）"""
    result = execute_d1_query("SELECT channel_id, is_target FROM is_target_channel")
    results = result.get("results", [])

    channels = {}
    for row in results:
        # channel_idは文字列として保存されているので、そのままintに変換
        channel_id = int(row["channel_id"])
        # D1は0/1を返すが、文字列の場合もあるので明示的に比較
        is_target = row["is_target"] in (1, "1", True)
        channels[channel_id] = is_target
        logger.debug(f"Loaded channel {channel_id}: is_target={is_target}")
    return channels


def save_channel_id(channel_id: int):
    """通知先チャンネルIDをD1に保存"""
    logger.debug(f"Saving channel_id: {channel_id}")
    result = execute_d1_query(
        "INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)",
        ["channel_id", str(channel_id)]
    )
    logger.debug(f"save_channel_id result: {result}")


def load_channel_id() -> Optional[int]:
    """通知先チャンネルIDをD1から読み込み"""
    result = execute_d1_query("SELECT value FROM bot_settings WHERE key = ?", ["channel_id"])
    results = result.get("results", [])

    if results and len(results) > 0:
        return int(results[0]["value"])

    return None


def save_call_end_notification_enabled(enabled: bool):
    """終了通知設定をD1に保存"""
    logger.debug(f"Saving is_call_end_notification_enabled: {enabled}")
    result = execute_d1_query(
        "INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)",
        ["is_call_end_notification_enabled", "1" if enabled else "0"]
    )
    logger.debug(f"save_call_end_notification_enabled result: {result}")


def load_call_end_notification_enabled() -> Optional[bool]:
    """終了通知設定をD1から読み込み"""
    result = execute_d1_query("SELECT value FROM bot_settings WHERE key = ?", ["is_call_end_notification_enabled"])
    results = result.get("results", [])

    if results and len(results) > 0:
        return results[0]["value"] == "1"

    return None
