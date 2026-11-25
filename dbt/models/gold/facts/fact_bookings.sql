{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_bookings') }}

),

customer AS (

    SELECT *
    FROM {{ ref('dim_customer') }}

),

date_dim AS (

    SELECT *
    FROM {{ ref('dim_date') }}

),

final AS (

    SELECT
        -- Primary key
        {{ dbt_utils.generate_surrogate_key(['b.BOOKING_ID']) }}
            AS BOOKING_KEY,

        -- Business identifiers
        b.BOOKING_ID,
        b.BOOKING_REFERENCE,
        b.CUSTOMER_ID,

        -- Foreign keys
        COALESCE(c.CUSTOMER_KEY, 'UNKNOWN')
            AS CUSTOMER_KEY,

        d.DATE_KEY AS BOOKING_DATE_KEY,

        -- Booking attributes
        b.BOOKING_CREATED_AT_UTC,
        b.BOOKING_CREATED_AT_SYD,
        CAST(b.BOOKING_CREATED_AT_SYD AS DATE)
            AS BOOKING_DATE,

        b.BOOKING_STATUS,
        b.CHANNEL,
        b.COUNTRY_CODE,
        b.CURRENCY_CODE,

        -- Measures
        1 AS BOOKING_COUNT,

        -- Data quality flags
        c.CUSTOMER_KEY IS NOT NULL
            AND c.CUSTOMER_KEY <> 'UNKNOWN'
            AS HAS_VALID_CUSTOMER,

        b.IS_VALID_BOOKING_DATE,
        d.DATE_KEY IS NOT NULL AS HAS_VALID_DATE_KEY,

        b.UPDATED_AT_UTC

    FROM source b

    LEFT JOIN customer c
        ON b.CUSTOMER_ID = c.CUSTOMER_ID

    LEFT JOIN date_dim d
        ON CAST(b.BOOKING_CREATED_AT_SYD AS DATE)
            = d.FULL_DATE

)

SELECT *
FROM final