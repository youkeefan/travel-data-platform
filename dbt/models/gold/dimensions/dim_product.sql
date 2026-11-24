{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_products') }}

),

category AS (

    SELECT *
    FROM {{ ref('dim_category') }}

),

vendor AS (

    SELECT *
    FROM {{ ref('dim_vendor') }}

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['p.PRODUCT_BK']) }}
            AS PRODUCT_KEY,

        p.PRODUCT_BK,
        p.PRODUCT_NAME,

        -- Category relationship
        c.CATEGORY_KEY,
        p.CATEGORY_BK,

        -- Vendor relationship
        v.VENDOR_KEY,
        p.VENDOR_BK,

        -- Product attributes
        p.DESTINATION,
        p.PRODUCT_STATUS,
        p.CREATED_AT_UTC,
        p.UPDATED_AT_UTC

    FROM source p

    LEFT JOIN category c
        ON p.CATEGORY_BK = c.CATEGORY_BK

    LEFT JOIN vendor v
        ON p.VENDOR_BK = v.VENDOR_BK

)

SELECT *
FROM final