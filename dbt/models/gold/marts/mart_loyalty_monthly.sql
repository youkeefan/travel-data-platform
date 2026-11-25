{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('fact_points_ledger') }}

    WHERE IS_VALID_POINTS_MOVEMENT = TRUE
        AND IS_FUTURE_EVENT = FALSE
        AND HAS_VALID_DATE_KEY = TRUE
        AND HAS_VALID_CUSTOMER = TRUE

),

monthly AS (

    SELECT
        DATE_TRUNC('MONTH', EVENT_DATE)::DATE
            AS MONTH_START_DATE,

        CUSTOMER_KEY,

        COUNT(*) AS LOYALTY_EVENT_COUNT,

        SUM(POINTS_EARNED) AS POINTS_EARNED,
        SUM(POINTS_REDEEMED) AS POINTS_REDEEMED,
        SUM(POINTS_EXPIRED) AS POINTS_EXPIRED,
        SUM(POINTS_ADJUSTED) AS POINTS_ADJUSTED,
        SUM(POINTS_REVERSED) AS POINTS_REVERSED,

        SUM(CURRENT_POINTS_MOVEMENT)
            AS NET_POINTS_MOVEMENT

    FROM source

    GROUP BY 1, 2

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key([
            'm.MONTH_START_DATE',
            'm.CUSTOMER_KEY'
        ]) }} AS LOYALTY_MONTHLY_KEY,

        -- Date attributes
        m.MONTH_START_DATE,
        d.DATE_KEY AS MONTH_DATE_KEY,
        d.YEAR_MONTH,
        d.CALENDAR_YEAR,
        d.CALENDAR_QUARTER,
        d.MONTH_NUMBER,
        d.FINANCIAL_YEAR,
        d.FINANCIAL_QUARTER,

        -- Customer attributes
        m.CUSTOMER_KEY,
        c.CUSTOMER_ID,
        c.TIER_NAME,
        c.CUSTOMER_STATUS,
        c.COUNTRY_CODE,
        c.AGE_BAND,
        c.TENURE_BAND,

        -- Monthly loyalty metrics
        m.LOYALTY_EVENT_COUNT,
        m.POINTS_EARNED,
        m.POINTS_REDEEMED,
        m.POINTS_EXPIRED,
        m.POINTS_ADJUSTED,
        m.POINTS_REVERSED,
        m.NET_POINTS_MOVEMENT,

        -- Cumulative points movement
        SUM(m.NET_POINTS_MOVEMENT) OVER (
            PARTITION BY m.CUSTOMER_KEY
            ORDER BY m.MONTH_START_DATE
            ROWS BETWEEN UNBOUNDED PRECEDING
                AND CURRENT ROW
        ) AS CUMULATIVE_POINTS_MOVEMENT,

        -- Loyalty ratios
        ROUND(
            m.POINTS_EARNED
            / NULLIF(m.POINTS_REDEEMED, 0),
            6
        ) AS EARN_TO_BURN_RATIO,

        ROUND(
            m.POINTS_REDEEMED
            / NULLIF(m.POINTS_EARNED, 0),
            6
        ) AS REDEMPTION_TO_EARN_RATIO,

        -- Engagement indicators
        m.POINTS_EARNED > 0 AS HAS_EARNED,
        m.POINTS_REDEEMED > 0 AS HAS_REDEEMED,
        m.POINTS_EXPIRED > 0 AS HAS_EXPIRED

    FROM monthly m

    LEFT JOIN {{ ref('dim_customer') }} c
        ON m.CUSTOMER_KEY = c.CUSTOMER_KEY

    LEFT JOIN {{ ref('dim_date') }} d
        ON m.MONTH_START_DATE = d.FULL_DATE

)

SELECT *
FROM final