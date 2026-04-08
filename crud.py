import sqlite3
from models import ActIn, ActOut, ActShort, PartItemOut, WorkItemOut
from database import get_connection


# --- helpers --------------------------------------------------------------

def _build_act_out(act_row: sqlite3.Row, conn: sqlite3.Connection) -> ActOut:
    # fetch related rows for a single act
    parts = conn.execute(
        "SELECT * FROM parts WHERE act_id = ? ORDER BY position", (act_row["id"],)
    ).fetchall()

    works = conn.execute(
        "SELECT * FROM works WHERE act_id = ? ORDER BY position", (act_row["id"],)
    ).fetchall()

    return ActOut(
        **dict(act_row),
        parts=[PartItemOut(**dict(p)) for p in parts],
        works=[WorkItemOut(**dict(w)) for w in works],
    )


def _log(conn: sqlite3.Connection, action: str, entity: str, entity_id: int | None = None, details: str | None = None) -> None:
    conn.execute(
        "INSERT INTO audit_log (action, entity, entity_id, details) VALUES (?, ?, ?, ?)",
        (action, entity, entity_id, details),
    )


# --- create ---------------------------------------------------------------

def create_act(data: ActIn) -> ActOut:
    parts_total = sum(item.price * item.quantity for item in data.parts)
    works_total = sum(item.price * item.quantity for item in data.works)
    total = round(parts_total + works_total, 2)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO acts (act_date, car_info, driver_phone, boss_phone, driver_name, total_amount)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.act_date.isoformat(),
                data.car_info,
                data.driver_phone,
                data.boss_phone,
                data.driver_name,
                total,
            ),
        )
        act_id = cursor.lastrowid

        # insert parts
        for i, item in enumerate(data.parts, start=1):
            conn.execute(
                "INSERT INTO parts (act_id, position, name, price, quantity, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (act_id, i, item.name, item.price, item.quantity, round(item.price * item.quantity, 2)),
            )

        # insert works
        for i, item in enumerate(data.works, start=1):
            conn.execute(
                "INSERT INTO works (act_id, position, name, price, quantity, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (act_id, i, item.name, item.price, item.quantity, round(item.price * item.quantity, 2)),
            )

        _log(conn, "create", "act", act_id)

        act_row = conn.execute("SELECT * FROM acts WHERE id = ?", (act_id,)).fetchone()
        return _build_act_out(act_row, conn)


# --- read -----------------------------------------------------------------

def get_act(act_id: int) -> ActOut | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM acts WHERE id = ?", (act_id,)).fetchone()
        if row is None:
            return None
        return _build_act_out(row, conn)


def get_all_acts(limit: int = 100, offset: int = 0) -> list[ActShort]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, act_date, car_info, driver_name, total_amount, created_at FROM acts ORDER BY act_date DESC, id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [ActShort(**dict(r)) for r in rows]


def search_acts(query: str) -> list[ActShort]:
    # search by car info, driver name, or date (partial match)
    pattern = f"%{query}%"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, act_date, car_info, driver_name, total_amount, created_at
            FROM acts
            WHERE car_info LIKE ? OR driver_name LIKE ? OR act_date LIKE ?
            ORDER BY act_date DESC, id DESC
            """,
            (pattern, pattern, pattern),
        ).fetchall()
        return [ActShort(**dict(r)) for r in rows]


# --- update ---------------------------------------------------------------

def update_act(act_id: int, data: ActIn) -> ActOut | None:
    parts_total = sum(item.price * item.quantity for item in data.parts)
    works_total = sum(item.price * item.quantity for item in data.works)
    total = round(parts_total + works_total, 2)

    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM acts WHERE id = ?", (act_id,)).fetchone()
        if existing is None:
            return None

        conn.execute(
            """
            UPDATE acts
            SET act_date = ?, car_info = ?, driver_phone = ?, boss_phone = ?,
                driver_name = ?, total_amount = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (
                data.act_date.isoformat(),
                data.car_info,
                data.driver_phone,
                data.boss_phone,
                data.driver_name,
                total,
                act_id,
            ),
        )

        # replace all rows — simpler than diffing
        conn.execute("DELETE FROM parts WHERE act_id = ?", (act_id,))
        conn.execute("DELETE FROM works WHERE act_id = ?", (act_id,))

        for i, item in enumerate(data.parts, start=1):
            conn.execute(
                "INSERT INTO parts (act_id, position, name, price, quantity, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (act_id, i, item.name, item.price, item.quantity, round(item.price * item.quantity, 2)),
            )

        for i, item in enumerate(data.works, start=1):
            conn.execute(
                "INSERT INTO works (act_id, position, name, price, quantity, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (act_id, i, item.name, item.price, item.quantity, round(item.price * item.quantity, 2)),
            )

        _log(conn, "update", "act", act_id)

        act_row = conn.execute("SELECT * FROM acts WHERE id = ?", (act_id,)).fetchone()
        return _build_act_out(act_row, conn)


# --- delete ---------------------------------------------------------------

def delete_act(act_id: int) -> bool:
    # returns False if act was not found
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM acts WHERE id = ?", (act_id,)).fetchone()
        if existing is None:
            return False
        conn.execute("DELETE FROM acts WHERE id = ?", (act_id,))
        _log(conn, "delete", "act", act_id)
        return True


# --- audit log ------------------------------------------------------------

def get_audit_log(limit: int = 200) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# --- stats ----------------------------------------------------------------

def get_stats(period: str = "month") -> dict:
    # period: "day", "month", "year"
    period_map = {
        "day":   "strftime('%Y-%m-%d', act_date)",
        "month": "strftime('%Y-%m', act_date)",
        "year":  "strftime('%Y', act_date)",
    }
    group_by = period_map.get(period, period_map["month"])

    with get_connection() as conn:
        revenue_rows = conn.execute(
            f"SELECT {group_by} as period, SUM(total_amount) as total FROM acts GROUP BY period ORDER BY period DESC LIMIT 24"
        ).fetchall()

        total_acts = conn.execute("SELECT COUNT(*) FROM acts").fetchone()[0]
        total_revenue = conn.execute("SELECT SUM(total_amount) FROM acts").fetchone()[0] or 0

        top_cars = conn.execute(
            "SELECT car_info, COUNT(*) as visits FROM acts GROUP BY car_info ORDER BY visits DESC LIMIT 10"
        ).fetchall()

    return {
        "revenue_by_period": [dict(r) for r in revenue_rows],
        "total_acts": total_acts,
        "total_revenue": round(total_revenue, 2),
        "top_cars": [dict(r) for r in top_cars],
    }