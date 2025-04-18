import sqlite3

DB_PATH = "db/bot_data.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # notitext テーブル
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notitext (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    """
    )
    # is_target_channel テーブル
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS is_target_channel (
            channel_id INTEGER PRIMARY KEY,
            is_target BOOLEAN NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def save_notitext(text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notitext")  # 古い値を削除
    cursor.execute("INSERT INTO notitext (text) VALUES (?)", (text,))
    conn.commit()
    conn.close()


def load_notitext():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM notitext LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "@everyone"  # デフォルト値


def save_is_target_channel(channel_id, is_target):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO is_target_channel (channel_id, is_target)
        VALUES (?, ?)
    """,
        (channel_id, is_target),
    )
    conn.commit()
    conn.close()


def load_is_target_channels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, is_target FROM is_target_channel")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: bool(row[1]) for row in rows}
