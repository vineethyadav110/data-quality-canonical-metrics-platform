import re

import sqlglot
from sqlglot import exp


# ---------------------------------------------------------
# Approved canonical tables
# ---------------------------------------------------------

ALLOWED_TABLES = {
    "fct_trip_metrics",
    "data_quality_metrics",
}


# ---------------------------------------------------------
# Approved columns
# ---------------------------------------------------------

ALLOWED_COLUMNS = {
    "fct_trip_metrics": {
        "trip_date",
        "total_trips",
        "completed_trips",
        "cancelled_trips",
        "in_progress_trips",
        "completion_rate",
        "avg_duration_seconds",
        "avg_distance_miles",
        "total_distance_miles",
        "total_revenue",
        "revenue_per_mile",
        "active_vehicles",
        "pipeline_run_id",
    },
    "data_quality_metrics": {
        "pipeline_date",
        "pipeline_runs",
        "raw_records",
        "clean_records",
        "failed_records",
        "quality_failure_rate",
        "runs_with_quarantine",
    },
}


# ---------------------------------------------------------
# Dangerous SQL operations
# ---------------------------------------------------------

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "MERGE",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "REPLACE",
}


def _remove_comments(sql: str) -> str:
    """
    Remove SQL comments before validation.
    """

    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)

    sql = re.sub(
        r"--.*?$",
        " ",
        sql,
        flags=re.MULTILINE,
    )

    return sql.strip()


def _normalize_table_name(table: exp.Table) -> str:
    """
    Return the base table name in lowercase.

    Works for both:
        fct_trip_metrics

    and later:
        DQ_ANALYTICS.ANALYTICS.FCT_TRIP_METRICS
    """

    return table.name.lower().strip()


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate an LLM-generated SQL statement.

    Rules:
    - Exactly one SQL statement.
    - SELECT/WITH queries only.
    - No destructive operations.
    - Only approved canonical tables.
    - Only approved columns.
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    # -----------------------------------------------------
    # Remove comments
    # -----------------------------------------------------

    cleaned_sql = _remove_comments(sql)
    

    if not cleaned_sql:
        return False, "SQL query is empty after removing comments."
        
    # -----------------------------------------------------
    # Reject SQL parameter placeholders
    # -----------------------------------------------------

    if "?" in cleaned_sql:
        return (
            False,
            "SQL parameter placeholder '?' is not allowed."
        )

    # -----------------------------------------------------
    # Prevent multiple statements
    # -----------------------------------------------------

    statements = sqlglot.parse(cleaned_sql, read="sqlite")

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    statement = statements[0]

    # -----------------------------------------------------
    # Only SELECT / WITH queries
    # -----------------------------------------------------

    if not isinstance(statement, exp.Query):
        return False, "Only read-only SELECT queries are allowed."

    # -----------------------------------------------------
    # Reject destructive operations
    # -----------------------------------------------------

    normalized_sql = cleaned_sql.upper()

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, normalized_sql):
            return (
                False,
                f"Forbidden SQL operation detected: {keyword}",
            )

    # -----------------------------------------------------
    # Validate tables
    # -----------------------------------------------------

    table_nodes = list(statement.find_all(exp.Table))

    # CTE names are allowed as temporary query objects
    cte_names = {
        cte.alias_or_name.lower()
        for cte in statement.find_all(exp.CTE)
    }

    for table in table_nodes:

        table_name = _normalize_table_name(table)

        # Ignore references to CTEs
        if table_name in cte_names:
            continue

        if table_name not in ALLOWED_TABLES:
            return (
                False,
                f"Unauthorized table detected: {table_name}",
            )

    # -----------------------------------------------------
    # Validate columns
    # -----------------------------------------------------

    allowed_columns = set()

    for columns in ALLOWED_COLUMNS.values():
        allowed_columns.update(columns)

    for column in statement.find_all(exp.Column):

        column_name = column.name.lower().strip()

        # Ignore wildcard SELECT *
        if column_name == "*":
            continue

        if column_name not in allowed_columns:
            return (
                False,
                f"Unauthorized column detected: {column_name}",
            )

    return True, "SQL validation passed."