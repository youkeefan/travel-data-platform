{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('fact_booking_items') }}

    WHERE GROSS_SALES_AUD > 0

),

aggregated AS (

    SELECT
        TRANSACTION_DATE_KEY,
        TRANSACTION_DATE,
        PRODUCT_KEY,

        COUNT(*) AS BOOKING_ITEM_COUNT,

        COUNT(DISTINCT BOOKING_ID)
            AS DISTINCT_BOOKING_COUNT,

        COUNT(DISTINCT CASE
            WHEN HAS_VALID_CUSTOMER
            THEN CUSTOMER_KEY
        END) AS DISTINCT_CUSTOMER_COUNT,

        SUM(GROSS_SALES_AUD) AS GROSS_SALES_AUD,
        SUM(GROSS_MARGIN_AUD) AS GROSS_MARGIN_AUD,
        SUM(DISCOUNT_AUD) AS DISCOUNT_AUD,
        SUM(REFUND_AUD) AS REFUND_AUD,

        SUM(ROOM_NIGHTS) AS ROOM_NIGHTS,
        SUM(TRAVELLER_COUNT) AS TRAVELLER_COUNT

    FROM source

    GROUP BY 1, 2, 3

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key([
            'a.TRANSACTION_DATE_KEY',
            'a.PRODUCT_KEY'
        ]) }} AS COMMERCIAL_DAILY_KEY,

        -- Date attributes
        a.TRANSACTION_DATE_KEY,
        a.TRANSACTION_DATE,
        d.CALENDAR_YEAR,
        d.CALENDAR_QUARTER,
        d.MONTH_NUMBER,
        d.YEAR_MONTH,
        d.FINANCIAL_YEAR,
        d.FINANCIAL_QUARTER,

        -- Product attributes
        a.PRODUCT_KEY,
        p.PRODUCT_NAME,
        p.DESTINATION,
        p.PRODUCT_STATUS,

        -- Category attributes
        p.CATEGORY_KEY,
        c.CATEGORY_NAME,
        c.CATEGORY_GROUP,

        -- Vendor attributes
        p.VENDOR_KEY,
        v.VENDOR_NAME,
        v.VENDOR_COUNTRY,

        -- Commercial measures
        a.BOOKING_ITEM_COUNT,
        a.DISTINCT_BOOKING_COUNT,
        a.DISTINCT_CUSTOMER_COUNT,

        a.GROSS_SALES_AUD,
        a.GROSS_MARGIN_AUD,
        a.DISCOUNT_AUD,
        a.REFUND_AUD,
        a.ROOM_NIGHTS,
        a.TRAVELLER_COUNT,

        -- Derived KPIs
        ROUND(
            a.GROSS_MARGIN_AUD
            / NULLIF(a.GROSS_SALES_AUD, 0),
            6
        ) AS GROSS_MARGIN_RATE,

        ROUND(
            a.GROSS_SALES_AUD
            / NULLIF(a.BOOKING_ITEM_COUNT, 0),
            2
        ) AS AVG_BOOKING_ITEM_VALUE_AUD

    FROM aggregated a

    LEFT JOIN {{ ref('dim_date') }} d
        ON a.TRANSACTION_DATE_KEY = d.DATE_KEY

    LEFT JOIN {{ ref('dim_product') }} p
        ON a.PRODUCT_KEY = p.PRODUCT_KEY

    LEFT JOIN {{ ref('dim_category') }} c
        ON p.CATEGORY_KEY = c.CATEGORY_KEY

    LEFT JOIN {{ ref('dim_vendor') }} v
        ON p.VENDOR_KEY = v.VENDOR_KEY

)

SELECT *
FROM final