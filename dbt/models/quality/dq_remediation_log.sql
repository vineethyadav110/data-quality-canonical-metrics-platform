{{ config(
    materialized='incremental',
    schema='QUALITY',
    unique_key='failure_key'
) }}

WITH failed AS (

    SELECT *
    FROM {{ ref('dq_failed_records') }}

),

remediable AS (

    SELECT
        failure_key,
        pipeline_run_id,
        record_hash,
        failure_reason,
        delivery_status

    FROM failed

    WHERE failure_reason IN (
        'invalid_delivery_status'
    )

),

final AS (

    SELECT
        failure_key,
        pipeline_run_id,
        record_hash,

        failure_reason AS rule_name,

        delivery_status AS original_value,

        CASE
            WHEN LOWER(TRIM(delivery_status)) = 'completeed'
                THEN 'completed'

            WHEN LOWER(TRIM(delivery_status)) = 'completed'
                THEN 'completed'

            WHEN LOWER(TRIM(delivery_status)) = 'cancelled'
                THEN 'cancelled'

            WHEN LOWER(TRIM(delivery_status)) = 'in_progress'
                THEN 'in_progress'

            ELSE NULL
        END AS corrected_value,

        'DETERMINISTIC_STATUS_NORMALIZATION'
            AS remediation_method,

        CURRENT_TIMESTAMP() AS remediated_at,

        CASE
            WHEN LOWER(TRIM(delivery_status)) IN (
                'completeed',
                'completed',
                'cancelled',
                'in_progress'
            )
            THEN 'REMEDIATED'

            ELSE 'OPEN'
        END AS status

    FROM remediable
)

SELECT *
FROM final

{% if is_incremental() %}

WHERE remediated_at >
    (SELECT COALESCE(MAX(remediated_at), '1900-01-01')
     FROM {{ this }})

{% endif %}