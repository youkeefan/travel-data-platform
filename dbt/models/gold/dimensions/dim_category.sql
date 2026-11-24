{{ config(materialized='table') }}

WITH source AS (

    SELECT *
    FROM {{ ref('stg_categories') }}

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['CATEGORY_BK']) }}
            AS CATEGORY_KEY,

        CATEGORY_BK,
        CATEGORY_NAME,
        CATEGORY_GROUP

    FROM source

)

SELECT *
FROM final