import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "analytics.db"
)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def execute_query(sql: str):

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(sql)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()