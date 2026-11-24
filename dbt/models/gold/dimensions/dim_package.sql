{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_packages') }}

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['PACKAGE_BK']) }}
            AS PACKAGE_KEY,

        PACKAGE_BK,
        PACKAGE_NAME,
        PACKAGE_TYPE,
        CREATED_AT_UTC,
        UPDATED_AT_UTC

    FROM source

)

SELECT *
FROM final