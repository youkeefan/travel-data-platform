{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_offers') }}

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['OFFER_BK']) }}
            AS OFFER_KEY,

        OFFER_BK,
        OFFER_NAME,
        OFFER_TYPE,
        DISCOUNT_AMOUNT,
        START_DATE,
        END_DATE,
        OFFER_STATUS,

        DATEDIFF('day', START_DATE, END_DATE) + 1
            AS OFFER_DURATION_DAYS,

        CASE
            WHEN START_DATE IS NULL OR END_DATE IS NULL
                THEN 'UNKNOWN'
            WHEN END_DATE < START_DATE
                THEN 'INVALID'
            WHEN CURRENT_DATE() < START_DATE
                THEN 'UPCOMING'
            WHEN CURRENT_DATE() > END_DATE
                THEN 'EXPIRED'
            ELSE 'CURRENT'
        END AS OFFER_LIFECYCLE_STATUS

    FROM source

)

SELECT *
FROM final