{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_vendors') }}

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['VENDOR_BK']) }}
            AS VENDOR_KEY,

        VENDOR_BK,
        VENDOR_NAME,
        VENDOR_COUNTRY,
        VENDOR_STATUS,
        UPDATED_AT_UTC

    FROM source

)

SELECT *
FROM final