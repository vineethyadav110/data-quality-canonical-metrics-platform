import time
import uuid
from datetime import datetime, timezone

from ai_assistant.database.local import DB_PATH


def get_audit_connection():
    import sqlite3

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_audit_table():
    """
    Create the AI query audit table if it does not already exist.
    """

    connection = get_audit_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_query_audit (
                request_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                normalized_question TEXT,
                generated_sql TEXT,
                validation_status TEXT,
                validation_message TEXT,
                execution_status TEXT,
                execution_error TEXT,
                row_count INTEGER,
                execution_time_ms REAL,
                answer TEXT,
                model TEXT,
                database_dialect TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def create_request_id():
    """
    Generate a unique ID for each assistant request.
    """

    return str(uuid.uuid4())


def save_audit_record(
    request_id: str,
    question: str,
    normalized_question: str | None = None,
    generated_sql: str | None = None,
    validation_status: str | None = None,
    validation_message: str | None = None,
    execution_status: str | None = None,
    execution_error: str | None = None,
    row_count: int | None = None,
    execution_time_ms: float | None = None,
    answer: str | None = None,
    model: str = "openai/gpt-oss-120b",
    database_dialect: str = "sqlite",
):
    """
    Store one complete assistant request in the audit table.
    """

    connection = get_audit_connection()

    try:
        cursor = connection.cursor()

        created_at = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT OR REPLACE INTO ai_query_audit (
                request_id,
                question,
                normalized_question,
                generated_sql,
                validation_status,
                validation_message,
                execution_status,
                execution_error,
                row_count,
                execution_time_ms,
                answer,
                model,
                database_dialect,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                question,
                normalized_question,
                generated_sql,
                validation_status,
                validation_message,
                execution_status,
                execution_error,
                row_count,
                execution_time_ms,
                answer,
                model,
                database_dialect,
                created_at,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def get_recent_audit_records(limit: int = 10):
    """
    Retrieve the most recent assistant requests.
    """

    connection = get_audit_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                request_id,
                question,
                validation_status,
                execution_status,
                row_count,
                execution_time_ms,
                created_at
            FROM ai_query_audit
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()