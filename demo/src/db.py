import sqlite3


def get_demo_db() -> sqlite3.Connection:
    return sqlite3.connect("src/db/demo.db")
