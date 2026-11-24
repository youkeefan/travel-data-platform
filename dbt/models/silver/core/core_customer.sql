WITH customer_profile AS (

    SELECT *
    FROM {{ ref('stg_customer_profile') }}

),

customer_address AS (

    SELECT *
    FROM {{ ref('int_customer_address') }}

),

customer_tier AS (

    SELECT *
    FROM {{ ref('int_customer_tier') }}

),

customer_status AS (

    SELECT *
    FROM {{ ref('int_customer_status') }}

),

integrated AS (

    SELECT
        p.CUSTOMER_ID,
        p.FIRST_NAME,
        p.LAST_NAME,
        p.EMAIL,
        p.PHONE,
        p.DATE_OF_BIRTH,
        p.GENDER,
        p.COUNTRY_CODE AS PROFILE_COUNTRY_CODE,

        -- Current address
        a.ADDRESS_ID,
        a.ADDRESS_LINE_1,
        a.CITY,
        a.STATE,
        a.POSTCODE,
        a.COUNTRY_CODE AS ADDRESS_COUNTRY_CODE,
        a.VALID_FROM AS ADDRESS_VALID_FROM,

        -- Current loyalty tier
        t.TIER_HISTORY_ID,
        t.TIER_NAME,
        t.TIER_START_DATE,

        -- Current customer status
        s.STATUS_HISTORY_ID,
        s.CUSTOMER_STATUS,
        s.STATUS_START_DATE,

        -- Data completeness indicators
        a.CUSTOMER_ID IS NOT NULL AS HAS_CURRENT_ADDRESS,
        t.CUSTOMER_ID IS NOT NULL AS HAS_CURRENT_TIER,
        s.CUSTOMER_ID IS NOT NULL AS HAS_CURRENT_STATUS,

        -- Metadata
        p.CREATED_AT_UTC,
        GREATEST_IGNORE_NULLS(
            p.UPDATED_AT_UTC,
            a.UPDATED_AT_UTC,
            t.UPDATED_AT_UTC,
            s.UPDATED_AT_UTC
        ) AS UPDATED_AT_UTC

    FROM customer_profile p

    LEFT JOIN customer_address a
        ON p.CUSTOMER_ID = a.CUSTOMER_ID

    LEFT JOIN customer_tier t
        ON p.CUSTOMER_ID = t.CUSTOMER_ID

    LEFT JOIN customer_status s
        ON p.CUSTOMER_ID = s.CUSTOMER_ID

)

SELECT *
FROM integrated