{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_points_ledger') }}

),

base AS (

    SELECT
        *,

        CASE
            WHEN EVENT_TYPE = 'EARN'
                THEN POINTS_AMOUNT

            WHEN EVENT_TYPE IN ('REDEEM', 'EXPIRE')
                THEN -POINTS_AMOUNT

            WHEN EVENT_TYPE = 'ADJUSTMENT'
                AND ADJUSTMENT_DIRECTION = 'CREDIT'
                THEN POINTS_AMOUNT

            WHEN EVENT_TYPE = 'ADJUSTMENT'
                AND ADJUSTMENT_DIRECTION = 'DEBIT'
                THEN -POINTS_AMOUNT

        END AS BASE_POINTS_MOVEMENT

    FROM source

),

reversals AS (

    SELECT
        r.LEDGER_ID,

        o.EVENT_TYPE AS ORIGINAL_EVENT_TYPE,
        o.ADJUSTMENT_DIRECTION AS ORIGINAL_DIRECTION,

        -SIGN(o.BASE_POINTS_MOVEMENT) * r.POINTS_AMOUNT
            AS REVERSAL_POINTS_MOVEMENT,

        COALESCE(
            o.LEDGER_ID IS NOT NULL
            AND o.BASE_POINTS_MOVEMENT IS NOT NULL
            AND o.CUSTOMER_ID = r.CUSTOMER_ID
            AND o.POINTS_AMOUNT = r.POINTS_AMOUNT
            AND r.POINTS_AMOUNT > 0
            AND r.EVENT_DATE_UTC >= o.EVENT_DATE_UTC,
            FALSE
        ) AS IS_VALID_REVERSAL_REFERENCE

    FROM base r

    LEFT JOIN base o
        ON r.RELATED_LEDGER_ID = o.LEDGER_ID

    WHERE r.EVENT_TYPE = 'REVERSAL'

),

ranked_reversals AS (

    SELECT
        r.LEDGER_ID,

        ROW_NUMBER() OVER (
            PARTITION BY l.RELATED_LEDGER_ID
            ORDER BY
                l.EVENT_DATE_UTC,
                l.CREATED_AT_UTC,
                l.LEDGER_ID
        ) AS REVERSAL_SEQUENCE

    FROM reversals r

    INNER JOIN source l
        ON r.LEDGER_ID = l.LEDGER_ID

    WHERE r.IS_VALID_REVERSAL_REFERENCE = TRUE

),

enriched AS (

    SELECT
        -- Primary key
        {{ dbt_utils.generate_surrogate_key(['l.LEDGER_ID']) }}
            AS LEDGER_KEY,

        -- Business identifiers
        l.LEDGER_ID,
        l.SOURCE_LEDGER_ID,
        l.CUSTOMER_ID,
        l.BOOKING_ID,
        l.BOOKING_ITEM_ID,
        l.TRANSACTION_ID,
        l.RELATED_LEDGER_ID,

        -- Foreign keys
        COALESCE(c.CUSTOMER_KEY, 'UNKNOWN')
            AS CUSTOMER_KEY,

        b.BOOKING_KEY,
        i.BOOKING_ITEM_KEY,
        d.DATE_KEY AS EVENT_DATE_KEY,
        e.DATE_KEY AS EXPIRY_DATE_KEY,

        -- Event attributes
        l.EVENT_TYPE,
        l.ADJUSTMENT_DIRECTION,
        l.EVENT_DATE_UTC,
        l.EVENT_DATE_SYD,
        CAST(l.EVENT_DATE_SYD AS DATE) AS EVENT_DATE,
        l.EXPIRY_DATE,
        l.SOURCE_SYSTEM,

        -- Reversal attributes
        r.ORIGINAL_EVENT_TYPE,
        r.ORIGINAL_DIRECTION,
        rr.REVERSAL_SEQUENCE,

        -- Original points amount
        l.POINTS_AMOUNT,

        -- Signed points movement
        CASE
            WHEN l.EVENT_TYPE = 'REVERSAL'
                THEN r.REVERSAL_POINTS_MOVEMENT
            ELSE l.BASE_POINTS_MOVEMENT
        END AS SIGNED_POINTS_MOVEMENT,

        1 AS EVENT_COUNT,

        -- Event validity flags
        COALESCE(
            l.EVENT_TYPE IN (
                'EARN', 'REDEEM', 'EXPIRE',
                'ADJUSTMENT', 'REVERSAL'
            ),
            FALSE
        ) AS IS_VALID_EVENT_TYPE,

        COALESCE(
            l.POINTS_AMOUNT > 0,
            FALSE
        ) AS IS_VALID_POINTS_AMOUNT,

        CASE
            WHEN l.EVENT_TYPE = 'ADJUSTMENT'
                THEN COALESCE(
                    l.ADJUSTMENT_DIRECTION IN ('CREDIT', 'DEBIT'),
                    FALSE
                )
            ELSE TRUE
        END AS IS_VALID_ADJUSTMENT_DIRECTION,

        CASE
            WHEN l.EVENT_TYPE = 'REVERSAL'
                THEN COALESCE(
                    r.IS_VALID_REVERSAL_REFERENCE,
                    FALSE
                )
            ELSE TRUE
        END AS IS_VALID_REVERSAL_REFERENCE,

        COALESCE(
            rr.REVERSAL_SEQUENCE > 1,
            FALSE
        ) AS IS_DUPLICATE_REVERSAL,

        -- Referential integrity flags
        c.CUSTOMER_KEY IS NOT NULL
            AND c.CUSTOMER_KEY <> 'UNKNOWN'
            AS HAS_VALID_CUSTOMER,

        l.BOOKING_ID IS NOT NULL
            AND b.BOOKING_KEY IS NULL
            AS IS_UNMATCHED_BOOKING,

        l.BOOKING_ITEM_ID IS NOT NULL
            AND i.BOOKING_ITEM_KEY IS NULL
            AS IS_UNMATCHED_BOOKING_ITEM,

        COALESCE(
            l.CUSTOMER_ID <> b.CUSTOMER_ID,
            FALSE
        ) AS IS_BOOKING_CUSTOMER_MISMATCH,

        COALESCE(
            l.CUSTOMER_ID <> i.CUSTOMER_ID,
            FALSE
        ) AS IS_ITEM_CUSTOMER_MISMATCH,

        COALESCE(
            l.BOOKING_ID <> i.BOOKING_ID,
            FALSE
        ) AS IS_BOOKING_ITEM_MISMATCH,

        -- Date validity flags
        d.DATE_KEY IS NOT NULL
            AS HAS_VALID_DATE_KEY,

        COALESCE(
            CAST(l.EVENT_DATE_SYD AS DATE) >
                CONVERT_TIMEZONE(
                    'Australia/Sydney',
                    CURRENT_TIMESTAMP()
                )::DATE,
            FALSE
        ) AS IS_FUTURE_EVENT,

        l.CREATED_AT_UTC,
        l.UPDATED_AT_UTC

    FROM base l

    LEFT JOIN reversals r
        ON l.LEDGER_ID = r.LEDGER_ID

    LEFT JOIN ranked_reversals rr
        ON l.LEDGER_ID = rr.LEDGER_ID

    LEFT JOIN {{ ref('dim_customer') }} c
        ON l.CUSTOMER_ID = c.CUSTOMER_ID

    LEFT JOIN {{ ref('fact_bookings') }} b
        ON l.BOOKING_ID = b.BOOKING_ID

    LEFT JOIN {{ ref('fact_booking_items') }} i
        ON l.BOOKING_ITEM_ID = i.BOOKING_ITEM_ID

    LEFT JOIN {{ ref('dim_date') }} d
        ON CAST(l.EVENT_DATE_SYD AS DATE) = d.FULL_DATE

    LEFT JOIN {{ ref('dim_date') }} e
        ON l.EXPIRY_DATE = e.FULL_DATE

),

validated AS (

    SELECT
        *,

        COALESCE(
            IS_VALID_EVENT_TYPE
            AND IS_VALID_POINTS_AMOUNT
            AND IS_VALID_ADJUSTMENT_DIRECTION
            AND IS_VALID_REVERSAL_REFERENCE
            AND NOT IS_DUPLICATE_REVERSAL
            AND SIGNED_POINTS_MOVEMENT IS NOT NULL,
            FALSE
        ) AS IS_VALID_POINTS_MOVEMENT

    FROM enriched

),

final AS (

    SELECT
        *,

        IFF(
            EVENT_TYPE = 'EARN',
            POINTS_AMOUNT,
            0
        ) AS POINTS_EARNED,

        IFF(
            EVENT_TYPE = 'REDEEM',
            POINTS_AMOUNT,
            0
        ) AS POINTS_REDEEMED,

        IFF(
            EVENT_TYPE = 'EXPIRE',
            POINTS_AMOUNT,
            0
        ) AS POINTS_EXPIRED,

        IFF(
            EVENT_TYPE = 'ADJUSTMENT',
            SIGNED_POINTS_MOVEMENT,
            0
        ) AS POINTS_ADJUSTED,

        IFF(
            EVENT_TYPE = 'REVERSAL',
            SIGNED_POINTS_MOVEMENT,
            0
        ) AS POINTS_REVERSED,

        IFF(
            IS_VALID_POINTS_MOVEMENT,
            SIGNED_POINTS_MOVEMENT,
            0
        ) AS VALIDATED_POINTS_MOVEMENT,

        IFF(
            IS_VALID_POINTS_MOVEMENT
            AND NOT IS_FUTURE_EVENT
            AND HAS_VALID_DATE_KEY,
            SIGNED_POINTS_MOVEMENT,
            0
        ) AS CURRENT_POINTS_MOVEMENT

    FROM validated

)

SELECT *
FROM final