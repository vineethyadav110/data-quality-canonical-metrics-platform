{{ config(
    materialized='view',
    schema='QUALITY'
) }}

WITH base AS (

    SELECT *
    FROM {{ ref('stg_trips') }}

),

duplicate_check AS (

    SELECT
        *,
        COUNT(*) OVER (
            PARTITION BY trip_id
        ) AS trip_id_count

    FROM base

),

quality AS (

    SELECT
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

        '{{ var("pipeline_run_id", "manual") }}' AS pipeline_run_id,

        SHA2(
            CONCAT_WS(
                '||',
                COALESCE(trip_id, ''),
                COALESCE(vehicle_id, ''),
                COALESCE(CAST(started_at AS VARCHAR), ''),
                COALESCE(CAST(completed_at AS VARCHAR), ''),
                COALESCE(CAST(distance_miles AS VARCHAR), ''),
                COALESCE(CAST(duration_seconds AS VARCHAR), ''),
                COALESCE(delivery_status, ''),
                COALESCE(CAST(fare_amount AS VARCHAR), ''),
                COALESCE(source_file, '')
            ),
            256
        ) AS record_hash,

        CASE
            WHEN trip_id IS NULL
                THEN 'missing_trip_id'

            WHEN trip_id_count > 1
                THEN 'duplicate_trip_id'

            WHEN vehicle_id IS NULL
                THEN 'missing_vehicle_id'

            WHEN distance_miles < 0
                THEN 'negative_distance'

            WHEN fare_amount < 0
                THEN 'negative_fare'

            WHEN duration_seconds <= 0
                THEN 'invalid_duration'

            WHEN completed_at < started_at
                THEN 'invalid_time_sequence'

            WHEN delivery_status NOT IN (
                'completed',
                'cancelled',
                'in_progress'
            )
                THEN 'invalid_delivery_status'

            ELSE NULL
        END AS failure_reason

    FROM duplicate_check

)

SELECT
    *,
    CASE
        WHEN failure_reason IS NULL
            THEN 'PASSED'
        ELSE 'FAILED'
    END AS quality_status
FROM quality