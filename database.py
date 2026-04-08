import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "autoservice.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # проверка внешних ключей
    conn.execute("PRAGMA journal_mode = WAL")  # защита от повреждения базы данных при сбоях
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS acts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                act_date     TEXT    NOT NULL,
                car_info     TEXT    NOT NULL,
                driver_phone TEXT,
                boss_phone   TEXT,
                driver_name  TEXT,
                total_amount REAL    NOT NULL DEFAULT 0,
                created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS parts (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                act_id    INTEGER NOT NULL REFERENCES acts(id) ON DELETE CASCADE,
                position  INTEGER NOT NULL,
                name      TEXT    NOT NULL,
                price     REAL    NOT NULL,
                quantity  REAL    NOT NULL DEFAULT 1,
                amount    REAL    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS works (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                act_id    INTEGER NOT NULL REFERENCES acts(id) ON DELETE CASCADE,
                position  INTEGER NOT NULL,
                name      TEXT    NOT NULL,
                price     REAL    NOT NULL,
                quantity  REAL    NOT NULL DEFAULT 1,
                amount    REAL    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                action     TEXT NOT NULL,
                entity     TEXT NOT NULL,
                entity_id  INTEGER,
                details    TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
        """)