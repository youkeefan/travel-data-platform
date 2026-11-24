SELECT
    'ADDRESS' AS SOURCE_TABLE,
    CUSTOMER_ID,
    IS_CURRENT
FROM {{ ref('stg_customer_address') }}
WHERE IS_CURRENT IS NULL

UNION ALL

SELECT
    'TIER',
    CUSTOMER_ID,
    IS_CURRENT
FROM {{ ref('stg_customer_tier_history') }}
WHERE IS_CURRENT IS NULL

UNION ALL

SELECT
    'STATUS',
    CUSTOMER_ID,
    IS_CURRENT
FROM {{ ref('stg_customer_status_history') }}
WHERE IS_CURRENT IS NULL
