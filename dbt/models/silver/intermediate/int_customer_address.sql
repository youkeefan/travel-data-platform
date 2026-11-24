WITH current_address AS (

    SELECT
        CUSTOMER_ID,
        ADDRESS_ID,
        ADDRESS_LINE_1,
        CITY,
        STATE,
        POSTCODE,
        COUNTRY_CODE,
        VALID_FROM,
        UPDATED_AT_UTC

    FROM {{ ref('stg_customer_address') }}

    WHERE IS_CURRENT = TRUE

)

SELECT *
FROM current_address