WITH current_status AS (

    SELECT
        CUSTOMER_ID,
        STATUS_HISTORY_ID,
        CUSTOMER_STATUS,
        START_DATE AS STATUS_START_DATE,
        UPDATED_AT_UTC

    FROM {{ ref('stg_customer_status_history') }}

    WHERE IS_CURRENT = TRUE

)

SELECT *
FROM current_status