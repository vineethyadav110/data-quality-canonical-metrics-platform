{{ config(
    materialized='table',
    schema='ANALYTICS'
) }}

SELECT
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
    loaded_at
FROM {{ ref('int_trip_quality') }}
WHERE quality_status = 'PASSED'