{{ config(materialized='table') }}

WITH source AS (

    SELECT
        *,
        CONVERT_TIMEZONE(
            'UTC',
            'Australia/Sydney',
            PAYMENT_DATE_UTC
        ) AS PAYMENT_DATE_SYD

    FROM {{ ref('stg_payments') }}

),

final AS (

    SELECT
        -- Primary key
        {{ dbt_utils.generate_surrogate_key(['p.PAYMENT_ID']) }}
            AS PAYMENT_KEY,

        -- Business identifiers
        p.PAYMENT_ID,
        p.BOOKING_ID,
        b.CUSTOMER_ID,
        p.TRANSACTION_REFERENCE,

        -- Foreign keys
        b.BOOKING_KEY,
        b.CUSTOMER_KEY,
        d.DATE_KEY AS PAYMENT_DATE_KEY,

        -- Payment attributes
        p.PAYMENT_DATE_UTC,
        p.PAYMENT_DATE_SYD,
        CAST(p.PAYMENT_DATE_SYD AS DATE) AS PAYMENT_DATE,
        UPPER(TRIM(p.PAYMENT_METHOD)) AS PAYMENT_METHOD,
        UPPER(TRIM(p.PAYMENT_STATUS)) AS PAYMENT_STATUS,
        p.CURRENCY_CODE,

        -- Financial measures
        p.PAYMENT_AMOUNT,

        CASE
            WHEN UPPER(TRIM(p.PAYMENT_STATUS)) = 'SUCCESSFUL'
                THEN p.PAYMENT_AMOUNT
            ELSE 0
        END AS SUCCESSFUL_PAYMENT_AMOUNT,

        -- Operational measures
        1 AS PAYMENT_COUNT,

        -- Business flags
        UPPER(TRIM(p.PAYMENT_STATUS)) = 'SUCCESSFUL'
            AS IS_SUCCESSFUL_PAYMENT,

        -- Data quality flags
        b.HAS_VALID_CUSTOMER,
        d.DATE_KEY IS NOT NULL AS HAS_VALID_DATE_KEY,

        p.CURRENCY_CODE = b.CURRENCY_CODE
            AS IS_CURRENCY_CONSISTENT,

        p.UPDATED_AT_UTC

    FROM source p

    LEFT JOIN {{ ref('fact_bookings') }} b
        ON p.BOOKING_ID = b.BOOKING_ID

    LEFT JOIN {{ ref('dim_date') }} d
        ON CAST(p.PAYMENT_DATE_SYD AS DATE) = d.FULL_DATE

)

SELECT *
FROM final