{{ config(
    materialized='view',
    schema='QUALITY'
) }}

WITH source_data AS (

    SELECT *
    FROM {{ ref('stg_trips') }}

),

remediated AS (

    SELECT
        trip_id,
        vehicle_id,
        started_at,
        completed_at,
        distance_miles,
        duration_seconds,

        CASE
            WHEN LOWER(TRIM(delivery_status)) IN ('completeed', 'completed')
                THEN 'completed'

            WHEN LOWER(TRIM(delivery_status)) = 'cancelled'
                THEN 'cancelled'

            WHEN LOWER(TRIM(delivery_status)) = 'in_progress'
                THEN 'in_progress'

            ELSE LOWER(TRIM(delivery_status))
        END AS delivery_status,

        fare_amount,
        source_file,
        loaded_at

    FROM source_data
)

SELECT *
FROM remediated
