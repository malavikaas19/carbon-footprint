import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "carbonlens.db"

def create_table():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                electricity REAL NOT NULL,
                vehicles INTEGER NOT NULL,
                solar REAL NOT NULL,
                ac_hours REAL NOT NULL,
                waste REAL NOT NULL,
                emissions REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)
        con.commit()

def save_record(electricity, vehicles, solar, ac_hours, waste, emissions):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO simulations (electricity, vehicles, solar, ac_hours, waste, emissions)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (float(electricity), int(vehicles), float(solar), float(ac_hours), float(waste), float(emissions)))
        con.commit()

def get_all_records():
    with sqlite3.connect(DB_PATH) as con:
        return con.execute("""
            SELECT id, electricity, vehicles, solar, ac_hours, waste, emissions, created_at
            FROM simulations ORDER BY id DESC
        """).fetchall()

def delete_all_records():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM simulations")
        con.commit()
