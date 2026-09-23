{{ config(
    materialized='table',
    schema='ANALYTICS'
) }}

WITH audit AS (

    SELECT *
    FROM {{ source('quality', 'pipeline_run_audit') }}

),

daily_quality AS (

    SELECT
        CAST(started_at AS DATE) AS pipeline_date,

        COUNT(*) AS pipeline_runs,

        SUM(raw_record_count) AS raw_records,

        SUM(clean_record_count) AS clean_records,

        SUM(failed_record_count) AS failed_records,

        ROUND(
            SUM(failed_record_count)
            / NULLIF(SUM(raw_record_count), 0),
            4
        ) AS quality_failure_rate,

        SUM(
            CASE
                WHEN status = 'SUCCESS_WITH_QUARANTINE'
                THEN 1
                ELSE 0
            END
        ) AS runs_with_quarantine

    FROM audit

    GROUP BY CAST(started_at AS DATE)

)

SELECT *
FROM daily_quality