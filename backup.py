import sqlite3
import csv
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH     = Path(__file__).parent / "autoservice.db"
BACKUP_DIR  = Path(__file__).parent / "backups"


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M")


def backup_db() -> Path:
    # copy the entire .db file — safest way, preserves everything
    BACKUP_DIR.mkdir(exist_ok=True)
    dest = BACKUP_DIR / f"autoservice_{timestamp()}.db"
    # sqlite3 online backup — safe even if server is running
    src_conn = sqlite3.connect(DB_PATH)
    dst_conn = sqlite3.connect(dest)
    src_conn.backup(dst_conn)
    src_conn.close()
    dst_conn.close()
    print(f"[OK] DB backup saved: {dest}")
    return dest


def backup_csv() -> list[Path]:
    # export each table to a separate csv file
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = timestamp()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    saved = []

    tables = ["acts", "parts", "works", "audit_log"]
    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        dest = BACKUP_DIR / f"{table}_{ts}.csv"
        with open(dest, "w", newline="", encoding="utf-8-sig") as f:
            # utf-8-sig adds BOM so Excel opens cyrillic correctly
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows([dict(r) for r in rows])
            else:
                f.write("no data\n")
        print(f"[OK] CSV backup saved: {dest}")
        saved.append(dest)

    conn.close()
    return saved


def cleanup_old_backups(keep: int = 30) -> None:
    # keep only the N most recent .db backups to avoid filling the disk
    db_backups = sorted(BACKUP_DIR.glob("autoservice_*.db"))
    to_delete = db_backups[:-keep] if len(db_backups) > keep else []
    for f in to_delete:
        f.unlink()
        print(f"[removed] {f.name}")


if __name__ == "__main__":
    print(f"Starting backup — {timestamp()}")
    backup_db()
    backup_csv()
    cleanup_old_backups(keep=30)
    print("Done.")