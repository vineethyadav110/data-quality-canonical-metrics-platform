METRIC_DEFINITIONS = {
    "total_trips": {
        "definition": "Count of valid analytical trip records.",
        "table": "fct_trip_metrics",
        "column": "total_trips",
        "dimensions": ["trip_date"]
    },

    "completed_trips": {
        "definition": "Trips where delivery_status is completed.",
        "table": "fct_trip_metrics",
        "column": "completed_trips",
        "dimensions": ["trip_date"]
    },

    "cancelled_trips": {
        "definition": "Trips where delivery_status is cancelled.",
        "table": "fct_trip_metrics",
        "column": "cancelled_trips",
        "dimensions": ["trip_date"]
    },

    "in_progress_trips": {
        "definition": "Trips currently in progress.",
        "table": "fct_trip_metrics",
        "column": "in_progress_trips",
        "dimensions": ["trip_date"]
    },

    "completion_rate": {
        "definition": "Completed trips divided by total trips.",
        "table": "fct_trip_metrics",
        "column": "completion_rate",
        "dimensions": ["trip_date"]
    },

    "avg_duration_seconds": {
        "definition": "Average trip duration in seconds.",
        "table": "fct_trip_metrics",
        "column": "avg_duration_seconds",
        "dimensions": ["trip_date"]
    },

    "avg_distance_miles": {
        "definition": "Average trip distance in miles.",
        "table": "fct_trip_metrics",
        "column": "avg_distance_miles",
        "dimensions": ["trip_date"]
    },

    "total_distance_miles": {
        "definition": "Total valid trip distance in miles.",
        "table": "fct_trip_metrics",
        "column": "total_distance_miles",
        "dimensions": ["trip_date"]
    },

    "total_revenue": {
        "definition": "Sum of revenue from valid analytical trips.",
        "table": "fct_trip_metrics",
        "column": "total_revenue",
        "dimensions": ["trip_date"]
    },

    "revenue_per_mile": {
        "definition": "Total revenue divided by total distance.",
        "table": "fct_trip_metrics",
        "column": "revenue_per_mile",
        "dimensions": ["trip_date"]
    },

    "active_vehicles": {
        "definition": "Number of active vehicles.",
        "table": "fct_trip_metrics",
        "column": "active_vehicles",
        "dimensions": ["trip_date"]
    },

    "quality_failure_rate": {
        "definition": "Failed records divided by raw records.",
        "table": "data_quality_metrics",
        "column": "quality_failure_rate",
        "dimensions": ["pipeline_date"]
    }
}


DIMENSION_DEFINITIONS = {
    "trip_date": {
        "definition": "Calendar date associated with the trip metrics.",
        "table": "fct_trip_metrics",
        "column": "trip_date",
        "data_type": "DATE"
    },

    "pipeline_date": {
        "definition": "Calendar date associated with the pipeline run.",
        "table": "data_quality_metrics",
        "column": "pipeline_date",
        "data_type": "DATE"
    }
}