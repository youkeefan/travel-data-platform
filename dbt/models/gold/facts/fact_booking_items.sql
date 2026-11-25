{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_booking_items') }}

),

final AS (

    SELECT
        -- Primary key
        {{ dbt_utils.generate_surrogate_key(['i.BOOKING_ITEM_ID']) }}
            AS BOOKING_ITEM_KEY,

        -- Business identifiers
        i.BOOKING_ITEM_ID,
        i.BOOKING_ID,
        b.CUSTOMER_ID,
        i.PRODUCT_BK,
        i.CATEGORY_BK,
        i.VENDOR_BK,
        i.OFFER_BK,
        i.PACKAGE_BK,

        -- Foreign keys
        b.BOOKING_KEY,
        b.CUSTOMER_KEY,
        d.DATE_KEY AS TRANSACTION_DATE_KEY,
        COALESCE(p.PRODUCT_KEY, 'UNKNOWN') AS PRODUCT_KEY,
        c.CATEGORY_KEY,
        v.VENDOR_KEY,
        o.OFFER_KEY,
        pk.PACKAGE_KEY,

        -- Transaction attributes
        i.TRANSACTION_DATE_UTC,
        i.TRANSACTION_DATE_SYD,
        CAST(i.TRANSACTION_DATE_SYD AS DATE) AS TRANSACTION_DATE,
        i.CHECK_IN_DATE,
        i.CHECK_OUT_DATE,

        -- Financial measures
        i.GROSS_SALES_AUD,
        i.GROSS_MARGIN_AUD,
        i.DISCOUNT_AUD,
        i.REFUND_AUD,

        -- Operational measures
        i.ROOM_NIGHTS,
        i.TRAVELLER_COUNT,
        1 AS BOOKING_ITEM_COUNT,

        -- Data quality flags
        b.HAS_VALID_CUSTOMER,

        p.PRODUCT_KEY IS NOT NULL
            AND p.PRODUCT_KEY <> 'UNKNOWN'
            AS HAS_VALID_PRODUCT,

        d.DATE_KEY IS NOT NULL AS HAS_VALID_DATE_KEY,

        i.UPDATED_AT_UTC

    FROM source i

    LEFT JOIN {{ ref('fact_bookings') }} b
        ON i.BOOKING_ID = b.BOOKING_ID

    LEFT JOIN {{ ref('dim_product') }} p
        ON i.PRODUCT_BK = p.PRODUCT_BK

    LEFT JOIN {{ ref('dim_category') }} c
        ON i.CATEGORY_BK = c.CATEGORY_BK

    LEFT JOIN {{ ref('dim_vendor') }} v
        ON i.VENDOR_BK = v.VENDOR_BK

    LEFT JOIN {{ ref('dim_offer') }} o
        ON i.OFFER_BK = o.OFFER_BK

    LEFT JOIN {{ ref('dim_package') }} pk
        ON i.PACKAGE_BK = pk.PACKAGE_BK

    LEFT JOIN {{ ref('dim_date') }} d
        ON CAST(i.TRANSACTION_DATE_SYD AS DATE) = d.FULL_DATE

)

SELECT *
FROM final