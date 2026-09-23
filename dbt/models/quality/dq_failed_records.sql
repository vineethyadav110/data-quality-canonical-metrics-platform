{{ config(
    materialized='incremental',
    schema='QUALITY',
    unique_key='failure_key',
    on_schema_change='sync_all_columns'
) }}

WITH failed AS (

    SELECT *
    FROM {{ ref('int_trip_quality') }}
    WHERE quality_status = 'FAILED'

),

final AS (

    SELECT
        SHA2(
            CONCAT_WS(
                '||',
                pipeline_run_id,
                record_hash,
                failure_reason
            ),
            256
        ) AS failure_key,

        pipeline_run_id,
        record_hash,

        trip_id,
        vehicle_id,
        started_at,
        completed_at,
        distance_miles,
        duration_seconds,
        delivery_status,
        fare_amount,
        source_file,
        loaded_at,

        failure_reason,

        'OPEN' AS remediation_status,

        CURRENT_TIMESTAMP() AS detected_at,

        CAST(NULL AS TIMESTAMP_NTZ) AS remediated_at

    FROM failed

)

SELECT *
FROM final
QUALIFY ROW_NUMBER() OVER (PARTITION BY failure_key ORDER BY detected_at DESC) = 1