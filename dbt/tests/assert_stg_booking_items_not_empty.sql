SELECT 1 AS validation_failure
WHERE (
    SELECT COUNT(*)
    FROM {{ ref('stg_booking_items') }}
) = 0