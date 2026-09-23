select
    cast(started_at as date) as metric_date,
    count(*) as total_trips,
    count_if(delivery_status = 'completed') as completed_trips,
    count_if(delivery_status = 'cancelled') as cancelled_trips,
    round(completed_trips / nullif(total_trips, 0), 4) as completion_rate,
    round(avg(duration_seconds), 2) as avg_trip_duration_seconds,
    round(avg(distance_miles), 2) as avg_distance_miles,
    round(sum(fare_amount), 2) as total_revenue
from {{ ref('fct_trips') }}
group by 1
order by 1
