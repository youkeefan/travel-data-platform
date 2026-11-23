
{{ config(materialized='view') }}

WITH invalid_dates AS (

    SELECT
        'customer_profile' AS SOURCE_TABLE,
        CUSTOMER_ID AS RECORD_ID,
        'DATE_OF_BIRTH' AS COLUMN_NAME,
        DATE_OF_BIRTH AS RAW_VALUE
    FROM {{ source('travel_bronze', 'customer_profile') }}
    WHERE DATE_OF_BIRTH IS NOT NULL
      AND TRY_TO_DATE(DATE_OF_BIRTH) IS NULL

    UNION ALL

    SELECT
        'customer_address',
        ADDRESS_ID,
        'VALID_FROM',
        VALID_FROM
    FROM {{ source('travel_bronze', 'customer_address') }}
    WHERE VALID_FROM IS NOT NULL
      AND TRY_TO_DATE(VALID_FROM) IS NULL

    UNION ALL

    SELECT
        'customer_tier_history',
        TIER_HISTORY_ID,
        'START_DATE',
        START_DATE
    FROM {{ source('travel_bronze', 'customer_tier_history') }}
    WHERE START_DATE IS NOT NULL
      AND TRY_TO_DATE(START_DATE) IS NULL

    UNION ALL

    SELECT
        'bookings',
        BOOKING_ID,
        'BOOKING_CREATED_AT_UTC',
        BOOKING_CREATED_AT_UTC
    FROM {{ source('travel_bronze', 'bookings') }}
    WHERE BOOKING_CREATED_AT_UTC IS NOT NULL
      AND TRY_TO_TIMESTAMP_NTZ(BOOKING_CREATED_AT_UTC) IS NULL

)

SELECT
    *,
    'INVALID_DATE_FORMAT' AS ERROR_REASON
FROM invalid_dates
