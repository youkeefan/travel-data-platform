WITH current_tier AS (

    SELECT
        CUSTOMER_ID,
        TIER_HISTORY_ID,
        TIER_NAME,
        START_DATE AS TIER_START_DATE,
        UPDATED_AT_UTC

    FROM {{ ref('stg_customer_tier_history') }}

    WHERE IS_CURRENT = TRUE

)

SELECT *
FROM current_tier