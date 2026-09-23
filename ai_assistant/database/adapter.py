import os

from dotenv import load_dotenv

from ai_assistant.database.local import (
    execute_query as execute_sqlite_query,
)
from ai_assistant.database.snowflake import (
    execute_query as execute_snowflake_query,
)


load_dotenv("ai_assistant/.env")


def get_active_dialect() -> str:
    """
    Return the active database dialect configured
    in ai_assistant/.env.
    """

    dialect = os.getenv(
        "DATABASE_DIALECT",
        "sqlite",
    ).strip().lower()

    if dialect not in {"sqlite", "snowflake"}:
        raise RuntimeError(
            f"Unsupported DATABASE_DIALECT: {dialect}. "
            "Supported values are 'sqlite' and 'snowflake'."
        )

    return dialect


def get_database_dialect() -> str:
    """
    Backward-compatible alias for existing application code.
    """

    return get_active_dialect()


def execute_query(sql: str):
    """
    Execute a read-only SQL query against the active database.
    """

    dialect = get_active_dialect()

    if dialect == "sqlite":
        return execute_sqlite_query(sql)

    if dialect == "snowflake":
        return execute_snowflake_query(sql)

    raise RuntimeError(
        f"Unsupported DATABASE_DIALECT: {dialect}"
    )
