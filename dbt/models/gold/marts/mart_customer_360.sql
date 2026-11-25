{{ config(materialized='table') }}

WITH customers AS (

    SELECT *
    FROM {{ ref('dim_customer') }}

    WHERE CUSTOMER_KEY <> 'UNKNOWN'

),

commercial AS (

    SELECT
        CUSTOMER_KEY,

        COUNT(DISTINCT BOOKING_ID)
            AS TOTAL_BOOKINGS,

        COUNT(*) AS TOTAL_BOOKING_ITEMS,

        MIN(TRANSACTION_DATE) AS FIRST_PURCHASE_DATE,
        MAX(TRANSACTION_DATE) AS LAST_PURCHASE_DATE,

        SUM(GROSS_SALES_AUD) AS LIFETIME_GROSS_SALES_AUD,
        SUM(GROSS_MARGIN_AUD) AS LIFETIME_GROSS_MARGIN_AUD,
        SUM(DISCOUNT_AUD) AS LIFETIME_DISCOUNT_AUD,

        SUM(ROOM_NIGHTS) AS TOTAL_ROOM_NIGHTS,
        SUM(TRAVELLER_COUNT) AS TOTAL_TRAVELLERS

    FROM {{ ref('fact_booking_items') }}

    WHERE GROSS_SALES_AUD > 0
        AND HAS_VALID_CUSTOMER = TRUE

    GROUP BY 1

),

loyalty AS (

    SELECT
        CUSTOMER_KEY,

        SUM(POINTS_EARNED) AS TOTAL_POINTS_EARNED,
        SUM(POINTS_REDEEMED) AS TOTAL_POINTS_REDEEMED,
        SUM(POINTS_EXPIRED) AS TOTAL_POINTS_EXPIRED,
        SUM(POINTS_ADJUSTED) AS TOTAL_POINTS_ADJUSTED,
        SUM(POINTS_REVERSED) AS TOTAL_POINTS_REVERSED,

        SUM(CURRENT_POINTS_MOVEMENT)
            AS NET_POINTS_MOVEMENT,

        COUNT(*) AS TOTAL_LOYALTY_EVENTS,

        MAX(EVENT_DATE) AS LAST_LOYALTY_ACTIVITY_DATE

    FROM {{ ref('fact_points_ledger') }}

    WHERE IS_VALID_POINTS_MOVEMENT = TRUE
        AND IS_FUTURE_EVENT = FALSE
        AND HAS_VALID_DATE_KEY = TRUE
        AND HAS_VALID_CUSTOMER = TRUE

    GROUP BY 1

),

combined AS (

    SELECT
        -- Customer identifiers
        c.CUSTOMER_KEY,
        c.CUSTOMER_ID,

        -- Customer profile
        c.AGE,
        c.AGE_BAND,
        c.GENDER,
        c.COUNTRY_CODE,
        c.CITY,
        c.STATE,

        -- Membership attributes
        c.TIER_NAME,
        c.CUSTOMER_STATUS,
        c.CUSTOMER_SINCE,
        c.TENURE_DAYS,
        c.TENURE_BAND,

        -- Commercial activity
        COALESCE(s.TOTAL_BOOKINGS, 0)
            AS TOTAL_BOOKINGS,

        COALESCE(s.TOTAL_BOOKING_ITEMS, 0)
            AS TOTAL_BOOKING_ITEMS,

        s.FIRST_PURCHASE_DATE,
        s.LAST_PURCHASE_DATE,

        COALESCE(s.LIFETIME_GROSS_SALES_AUD, 0)
            AS LIFETIME_GROSS_SALES_AUD,

        COALESCE(s.LIFETIME_GROSS_MARGIN_AUD, 0)
            AS LIFETIME_GROSS_MARGIN_AUD,

        COALESCE(s.LIFETIME_DISCOUNT_AUD, 0)
            AS LIFETIME_DISCOUNT_AUD,

        COALESCE(s.TOTAL_ROOM_NIGHTS, 0)
            AS TOTAL_ROOM_NIGHTS,

        COALESCE(s.TOTAL_TRAVELLERS, 0)
            AS TOTAL_TRAVELLERS,

        -- Loyalty activity
        COALESCE(l.TOTAL_POINTS_EARNED, 0)
            AS TOTAL_POINTS_EARNED,

        COALESCE(l.TOTAL_POINTS_REDEEMED, 0)
            AS TOTAL_POINTS_REDEEMED,

        COALESCE(l.TOTAL_POINTS_EXPIRED, 0)
            AS TOTAL_POINTS_EXPIRED,

        COALESCE(l.TOTAL_POINTS_ADJUSTED, 0)
            AS TOTAL_POINTS_ADJUSTED,

        COALESCE(l.TOTAL_POINTS_REVERSED, 0)
            AS TOTAL_POINTS_REVERSED,

        COALESCE(l.NET_POINTS_MOVEMENT, 0)
            AS NET_POINTS_MOVEMENT,

        COALESCE(l.TOTAL_LOYALTY_EVENTS, 0)
            AS TOTAL_LOYALTY_EVENTS,

        l.LAST_LOYALTY_ACTIVITY_DATE,

        CONVERT_TIMEZONE(
            'Australia/Sydney',
            CURRENT_TIMESTAMP()
        )::DATE AS AS_OF_DATE

    FROM customers c

    LEFT JOIN commercial s
        ON c.CUSTOMER_KEY = s.CUSTOMER_KEY

    LEFT JOIN loyalty l
        ON c.CUSTOMER_KEY = l.CUSTOMER_KEY

),

final AS (

    SELECT
        *,

        -- RFM metrics
        DATEDIFF(
            day,
            LAST_PURCHASE_DATE,
            AS_OF_DATE
        ) AS RECENCY_DAYS,

        TOTAL_BOOKINGS AS FREQUENCY,

        LIFETIME_GROSS_SALES_AUD AS MONETARY_VALUE_AUD,

        -- Commercial KPIs
        ROUND(
            LIFETIME_GROSS_SALES_AUD
            / NULLIF(TOTAL_BOOKINGS, 0),
            2
        ) AS AVG_BOOKING_VALUE_AUD,

        ROUND(
            LIFETIME_GROSS_MARGIN_AUD
            / NULLIF(LIFETIME_GROSS_SALES_AUD, 0),
            6
        ) AS GROSS_MARGIN_RATE,

        -- Customer segmentation
        CASE
            WHEN TOTAL_BOOKINGS = 0
                THEN 'No Purchase'
            WHEN TOTAL_BOOKINGS = 1
                THEN 'Single Purchase'
            ELSE 'Repeat Customer'
        END AS PURCHASE_SEGMENT,

        TOTAL_BOOKINGS > 0 AS HAS_PURCHASED,

        TOTAL_BOOKINGS > 1 AS IS_REPEAT_CUSTOMER,

        TOTAL_LOYALTY_EVENTS > 0 AS HAS_LOYALTY_ACTIVITY

    FROM combined

)

SELECT *
FROM final