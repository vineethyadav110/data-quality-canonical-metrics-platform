import os
from pathlib import Path

import pendulum

# Airflow 3.x with fallback compatibility for Airflow 2.x
try:
    from airflow.sdk import dag
except ImportError:
    from airflow.decorators import dag

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.bash import BashOperator


# Resolve the repository root dynamically so the DAG does not depend
# on a developer-specific Mac path.
PROJECT_HOME = Path(__file__).resolve().parents[1]

# Allow an external dbt executable to be configured, while defaulting
# to the project's local virtual environment.
DBT_BIN = os.getenv(
    "DBT_BIN",
    str(PROJECT_HOME / ".venv" / "bin" / "dbt"),
)


@dag(
    dag_id="dq_canonical_metrics_pipeline",
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=[
        "dbt",
        "snowflake",
        "data-quality",
        "analytics-engineering",
    ],
)
def dq_canonical_metrics_pipeline():

    audit_start = SQLExecuteQueryOperator(
        task_id="audit_start",
        conn_id="snowflake_default",
        sql="""
            INSERT INTO DQ_ANALYTICS.QUALITY.PIPELINE_RUN_AUDIT (
                pipeline_run_id,
                started_at,
                status
            )
            VALUES (
                '{{ run_id }}',
                CURRENT_TIMESTAMP(),
                'STARTED'
            );
        """,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="""
            set -euo pipefail

            cd "$PROJECT_HOME"

            # Load local environment variables when running locally.
            # Secrets are never stored in the repository.
            if [ -f .env ]; then
                set -a
                source .env
                set +a
            fi

            "$DBT_BIN" build \
                --project-dir dbt \
                --vars '{"pipeline_run_id": "{{ run_id }}"}'
        """,
        env={
            "PROJECT_HOME": str(PROJECT_HOME),
            "DBT_BIN": DBT_BIN,
        },
        append_env=True,
    )

    audit_complete = SQLExecuteQueryOperator(
        task_id="audit_complete",
        conn_id="snowflake_default",
        sql="""
            MERGE INTO DQ_ANALYTICS.QUALITY.PIPELINE_RUN_AUDIT target
            USING (
                SELECT
                    '{{ run_id }}' AS pipeline_run_id,
                    CURRENT_TIMESTAMP() AS completed_at,

                    (
                        SELECT COUNT(*)
                        FROM DQ_ANALYTICS.RAW.RAW_TRIPS
                    ) AS raw_record_count,

                    (
                        SELECT COUNT(*)
                        FROM DQ_ANALYTICS.STAGING.STG_TRIPS
                    ) AS processed_record_count,

                    (
                        SELECT COUNT(*)
                        FROM DQ_ANALYTICS.ANALYTICS.FCT_TRIPS
                    ) AS clean_record_count,

                    (
                        SELECT COUNT(*)
                        FROM DQ_ANALYTICS.QUALITY.DQ_FAILED_RECORDS
                        WHERE pipeline_run_id = '{{ run_id }}'
                    ) AS failed_record_count
            ) source

            ON target.pipeline_run_id = source.pipeline_run_id

            WHEN MATCHED THEN UPDATE SET
                completed_at = source.completed_at,
                raw_record_count = source.raw_record_count,
                processed_record_count = source.processed_record_count,
                clean_record_count = source.clean_record_count,
                failed_record_count = source.failed_record_count,

                quality_failure_rate =
                    source.failed_record_count
                    / NULLIF(source.processed_record_count, 0),

                status =
                    CASE
                        WHEN source.failed_record_count = 0
                            THEN 'SUCCESS'
                        ELSE 'SUCCESS_WITH_QUARANTINE'
                    END;
        """,
    )

    audit_start >> dbt_build >> audit_complete


dq_canonical_metrics_pipeline()
