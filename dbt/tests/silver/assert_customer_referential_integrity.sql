SELECT
    'ADDRESS' AS SOURCE_TABLE,
    a.CUSTOMER_ID
FROM {{ ref('stg_customer_address') }} a
LEFT JOIN {{ ref('stg_customer_profile') }} p
    ON a.CUSTOMER_ID = p.CUSTOMER_ID
WHERE p.CUSTOMER_ID IS NULL

UNION ALL

SELECT
    'TIER',
    t.CUSTOMER_ID
FROM {{ ref('stg_customer_tier_history') }} t
LEFT JOIN {{ ref('stg_customer_profile') }} p
    ON t.CUSTOMER_ID = p.CUSTOMER_ID
WHERE p.CUSTOMER_ID IS NULL

UNION ALL

SELECT
    'STATUS',
    s.CUSTOMER_ID
FROM {{ ref('stg_customer_status_history') }} s
LEFT JOIN {{ ref('stg_customer_profile') }} p
    ON s.CUSTOMER_ID = p.CUSTOMER_ID
WHERE p.CUSTOMER_ID IS NULL
