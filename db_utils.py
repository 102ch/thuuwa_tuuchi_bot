import os
import requests
from typing import Optional, Dict, List

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
        print(f"D1 API request failed: {e}")
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
            channel_id INTEGER PRIMARY KEY,
            is_target BOOLEAN NOT NULL
        )
    """)
    print("D1 database initialized")


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
    """チャンネル設定をD1に保存"""
    execute_d1_query(
        "INSERT OR REPLACE INTO is_target_channel (channel_id, is_target) VALUES (?, ?)",
        [channel_id, 1 if is_target else 0]
    )


def load_is_target_channels() -> Dict[int, bool]:
    """全チャンネル設定をD1から読み込み"""
    result = execute_d1_query("SELECT channel_id, is_target FROM is_target_channel")
    results = result.get("results", [])

    return {
        int(row["channel_id"]): bool(row["is_target"])
        for row in results
    }
