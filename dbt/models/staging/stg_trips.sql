{{ config(
    materialized='view'
) }}

SELECT
    trip_id,
    vehicle_id,
    started_at,
    completed_at,
    distance_miles,
    duration_seconds,
    LOWER(TRIM(delivery_status)) AS delivery_status,
    fare_amount,
    source_file,
    loaded_at
FROM {{ source('raw', 'raw_trips') }}
