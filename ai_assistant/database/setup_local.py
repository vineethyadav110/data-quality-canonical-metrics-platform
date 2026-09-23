import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "analytics.db"
)


def setup():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        DROP TABLE IF EXISTS fct_trip_metrics
    """)

    cursor.execute("""
        CREATE TABLE fct_trip_metrics (
            trip_date TEXT,
            total_trips INTEGER,
            completed_trips INTEGER,
            cancelled_trips INTEGER,
            in_progress_trips INTEGER,
            completion_rate REAL,
            avg_duration_seconds REAL,
            avg_distance_miles REAL,
            total_distance_miles REAL,
            total_revenue REAL,
            revenue_per_mile REAL,
            active_vehicles INTEGER
        )
    """)

    data = [
        (
            "2026-09-14",
            1200, 1130, 50, 20,
            0.9417, 820, 4.8, 5760,
            8640, 1.50, 82
        ),
        (
            "2026-09-15",
            1350, 1275, 55, 20,
            0.9444, 810, 4.9, 6615,
            9922.5, 1.50, 85
        ),
        (
            "2026-09-16",
            1420, 1320, 75, 25,
            0.9296, 825, 4.7, 6674,
            10011, 1.50, 87
        ),
        (
            "2026-09-17",
            1500, 1330, 140, 30,
            0.8867, 850, 4.6, 6900,
            10350, 1.50, 89
        ),
        (
            "2026-09-18",
            1480, 1290, 160, 30,
            0.8716, 865, 4.5, 6660,
            9990, 1.50, 88
        )
    ]

    cursor.executemany("""
        INSERT INTO fct_trip_metrics
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    connection.commit()
    connection.close()

    print("Local analytics database created successfully.")


if __name__ == "__main__":
    setup()