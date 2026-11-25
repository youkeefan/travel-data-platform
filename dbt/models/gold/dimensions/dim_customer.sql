{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('core_customer') }}

),

transformed AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['CUSTOMER_ID']) }}
            AS CUSTOMER_KEY,

        CUSTOMER_ID,
        GENDER,

        -- Demographic attributes
        DATEDIFF('year', DATE_OF_BIRTH, CURRENT_DATE())
            - IFF(
                TO_CHAR(CURRENT_DATE(), 'MMDD')
                < TO_CHAR(DATE_OF_BIRTH, 'MMDD'),
                1, 0
            ) AS AGE,

        COALESCE(
            ADDRESS_COUNTRY_CODE,
            PROFILE_COUNTRY_CODE,
            'UNKNOWN'
        ) AS COUNTRY_CODE,

        CITY,
        STATE,

        -- Loyalty attributes
        COALESCE(TIER_NAME, 'UNKNOWN') AS TIER_NAME,
        TIER_START_DATE,
        COALESCE(CUSTOMER_STATUS, 'UNKNOWN') AS CUSTOMER_STATUS,
        STATUS_START_DATE,

        -- Customer tenure
        CAST(CREATED_AT_UTC AS DATE) AS CUSTOMER_SINCE,

        DATEDIFF(
            'day', CREATED_AT_UTC, CURRENT_DATE()
        ) AS TENURE_DAYS,

        -- Data quality indicators
        HAS_CURRENT_ADDRESS,
        HAS_CURRENT_TIER,
        HAS_CURRENT_STATUS,

        UPDATED_AT_UTC

    FROM source

),

final AS (

    SELECT
        *,

        CASE
            WHEN AGE IS NULL OR AGE < 0 OR AGE > 120 THEN 'Unknown'
            WHEN AGE < 18 THEN 'Under 18'
            WHEN AGE < 25 THEN '18-24'
            WHEN AGE < 35 THEN '25-34'
            WHEN AGE < 45 THEN '35-44'
            WHEN AGE < 55 THEN '45-54'
            WHEN AGE < 65 THEN '55-64'
            ELSE '65+'
        END AS AGE_BAND,

        CASE
            WHEN TENURE_DAYS IS NULL OR TENURE_DAYS < 0 THEN 'Unknown'
            WHEN TENURE_DAYS < 365 THEN 'Under 1 year'
            WHEN TENURE_DAYS < 730 THEN '1-2 years'
            WHEN TENURE_DAYS < 1825 THEN '2-5 years'
            ELSE '5+ years'
        END AS TENURE_BAND

    FROM transformed

)

SELECT *
FROM final

UNION ALL

SELECT
    'UNKNOWN' AS CUSTOMER_KEY,
    'UNKNOWN' AS CUSTOMER_ID,
    'UNKNOWN' AS GENDER,
    NULL AS AGE,
    'UNKNOWN' AS COUNTRY_CODE,
    NULL AS CITY,
    NULL AS STATE,
    'UNKNOWN' AS TIER_NAME,
    NULL AS TIER_START_DATE,
    'UNKNOWN' AS CUSTOMER_STATUS,
    NULL AS STATUS_START_DATE,
    NULL AS CUSTOMER_SINCE,
    NULL AS TENURE_DAYS,
    FALSE AS HAS_CURRENT_ADDRESS,
    FALSE AS HAS_CURRENT_TIER,
    FALSE AS HAS_CURRENT_STATUS,
    NULL AS UPDATED_AT_UTC,
    'Unknown' AS AGE_BAND,
    'Unknown' AS TENURE_BAND