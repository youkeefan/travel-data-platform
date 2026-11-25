{{ config(materialized='table') }}

WITH source AS (

    SELECT
        *,
        CONVERT_TIMEZONE(
            'UTC',
            'Australia/Sydney',
            REFUND_DATE_UTC
        ) AS REFUND_DATE_SYD

    FROM {{ ref('stg_refunds') }}

),

enriched AS (

    SELECT
        -- Primary key
        {{ dbt_utils.generate_surrogate_key(['r.REFUND_ID']) }}
            AS REFUND_KEY,

        -- Business identifiers
        r.REFUND_ID,
        r.BOOKING_ID,
        r.PAYMENT_ID,
        b.CUSTOMER_ID,

        -- Foreign keys
        b.BOOKING_KEY,
        p.PAYMENT_KEY,
        b.CUSTOMER_KEY,
        d.DATE_KEY AS REFUND_DATE_KEY,

        -- Refund attributes
        r.REFUND_DATE_UTC,
        r.REFUND_DATE_SYD,
        CAST(r.REFUND_DATE_SYD AS DATE) AS REFUND_DATE,
        UPPER(TRIM(r.REFUND_REASON)) AS REFUND_REASON,
        UPPER(TRIM(r.REFUND_STATUS)) AS REFUND_STATUS,
        r.CURRENCY_CODE,

        -- Financial measures
        r.REFUND_AMOUNT,

        -- Operational measures
        1 AS REFUND_COUNT,

        -- Business flags
        UPPER(TRIM(r.REFUND_STATUS)) = 'COMPLETED'
            AS IS_COMPLETED_REFUND,

        -- Data quality flags
        r.REFUND_AMOUNT > 0
            AS IS_VALID_REFUND_AMOUNT,

        r.BOOKING_ID = p.BOOKING_ID
            AS IS_BOOKING_CONSISTENT,

        r.CURRENCY_CODE = p.CURRENCY_CODE
            AS IS_CURRENCY_CONSISTENT,

        CASE
            WHEN r.CURRENCY_CODE = p.CURRENCY_CODE
                AND r.BOOKING_ID = p.BOOKING_ID
            THEN r.REFUND_AMOUNT > p.PAYMENT_AMOUNT
        END AS IS_OVER_REFUND,

        p.IS_SUCCESSFUL_PAYMENT,

        r.REFUND_DATE_UTC >= p.PAYMENT_DATE_UTC
            AS IS_VALID_REFUND_TIMING,

        b.HAS_VALID_CUSTOMER,

        d.DATE_KEY IS NOT NULL
            AS HAS_VALID_DATE_KEY,

        r.UPDATED_AT_UTC

    FROM source r

    LEFT JOIN {{ ref('fact_bookings') }} b
        ON r.BOOKING_ID = b.BOOKING_ID

    LEFT JOIN {{ ref('fact_payments') }} p
        ON r.PAYMENT_ID = p.PAYMENT_ID

    LEFT JOIN {{ ref('dim_date') }} d
        ON CAST(r.REFUND_DATE_SYD AS DATE) = d.FULL_DATE

),

validated AS (

    SELECT
        *,

        COALESCE(
            IS_VALID_REFUND_AMOUNT
            AND IS_BOOKING_CONSISTENT
            AND IS_CURRENCY_CONSISTENT
            AND NOT IS_OVER_REFUND
            AND IS_SUCCESSFUL_PAYMENT
            AND IS_VALID_REFUND_TIMING,
            FALSE
        ) AS IS_VALID_REFUND

    FROM enriched

),

final AS (

    SELECT
        *,

        CASE
            WHEN IS_COMPLETED_REFUND
                THEN REFUND_AMOUNT
            ELSE 0
        END AS COMPLETED_REFUND_AMOUNT,

        CASE
            WHEN IS_COMPLETED_REFUND
                AND IS_VALID_REFUND
                THEN REFUND_AMOUNT
            ELSE 0
        END AS VALIDATED_COMPLETED_REFUND_AMOUNT

    FROM validated

)

SELECT *
FROM final