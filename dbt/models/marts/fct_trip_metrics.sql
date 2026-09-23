{{ config(
    materialized='table',
    schema='ANALYTICS'
) }}

WITH clean_trips AS (

    SELECT *
    FROM {{ ref('fct_trips') }}

),

metrics AS (

    SELECT
        CAST(started_at AS DATE) AS trip_date,

        COUNT(*) AS total_trips,

        COUNT_IF(delivery_status = 'completed')
            AS completed_trips,

        COUNT_IF(delivery_status = 'cancelled')
            AS cancelled_trips,

        COUNT_IF(delivery_status = 'in_progress')
            AS in_progress_trips,

        ROUND(
            COUNT_IF(delivery_status = 'completed')
            / NULLIF(COUNT(*), 0),
            4
        ) AS completion_rate,

        ROUND(
            AVG(duration_seconds),
            2
        ) AS avg_duration_seconds,

        ROUND(
            AVG(distance_miles),
            2
        ) AS avg_distance_miles,

        ROUND(
            SUM(distance_miles),
            2
        ) AS total_distance_miles,

        ROUND(
            SUM(fare_amount),
            2
        ) AS total_revenue,

        ROUND(
            SUM(fare_amount)
            / NULLIF(SUM(distance_miles), 0),
            2
        ) AS revenue_per_mile,

        COUNT(DISTINCT vehicle_id)
            AS active_vehicles,

        MAX(pipeline_run_id)
            AS pipeline_run_id

    FROM clean_trips

    GROUP BY CAST(started_at AS DATE)

)

SELECT *
FROM metrics