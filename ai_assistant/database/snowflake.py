import os

from dotenv import load_dotenv

load_dotenv("ai_assistant/.env")


def get_connection():
    try:
        import snowflake.connector
    except ImportError as error:
        raise RuntimeError(
            "snowflake-connector-python is not installed. "
            "Run: pip install snowflake-connector-python"
        ) from error

    required_variables = {
        "SNOWFLAKE_ACCOUNT": os.getenv("SNOWFLAKE_ACCOUNT"),
        "SNOWFLAKE_USER": os.getenv("SNOWFLAKE_USER"),
        "SNOWFLAKE_PASSWORD": os.getenv("SNOWFLAKE_PASSWORD"),
        "SNOWFLAKE_WAREHOUSE": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "SNOWFLAKE_DATABASE": os.getenv("SNOWFLAKE_DATABASE"),
        "SNOWFLAKE_SCHEMA": os.getenv("SNOWFLAKE_SCHEMA"),
    }

    missing = [
        name
        for name, value in required_variables.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing Snowflake environment variables: "
            + ", ".join(missing)
        )

    connection_parameters = {
        "account": required_variables["SNOWFLAKE_ACCOUNT"],
        "user": required_variables["SNOWFLAKE_USER"],
        "password": required_variables["SNOWFLAKE_PASSWORD"],
        "warehouse": required_variables["SNOWFLAKE_WAREHOUSE"],
        "database": required_variables["SNOWFLAKE_DATABASE"],
        "schema": required_variables["SNOWFLAKE_SCHEMA"],
    }

    role = os.getenv("SNOWFLAKE_ROLE")
    if role:
        connection_parameters["role"] = role

    return snowflake.connector.connect(
        **connection_parameters
    )


def execute_query(sql: str):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(sql)

            columns = [
                column[0].lower()
                for column in cursor.description
            ]

            rows = cursor.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]

        finally:
            cursor.close()

    finally:
        connection.close()