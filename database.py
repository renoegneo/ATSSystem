import sqlite3
import bcrypt
from pathlib import Path

DB_PATH = Path(__file__).parent / "autoservice.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _default_hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


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

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

    # insert default credentials only if they don't exist yet
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("user_password_hash", _default_hash("1234")),
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("admin_password_hash", _default_hash("admin")),
        )


def get_setting(key: str) -> str | None:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )