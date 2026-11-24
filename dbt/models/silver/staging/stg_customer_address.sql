{% set source_relation = source('travel_bronze', 'customer_address') %}
{% set columns = adapter.get_columns_in_relation(source_relation) %}

WITH cleaned AS (

    SELECT
{% for col in columns %}
        {% set name = col.name | upper %}
        {% if name in [] %}
        TRY_TO_DECIMAL(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''), 18, 2)
            AS {{ adapter.quote(col.name) }}
        {% elif name in ['VALID_FROM', 'VALID_TO'] %}
        TRY_TO_DATE(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''))
            AS {{ adapter.quote(col.name) }}
        {% elif name in ['UPDATED_AT_UTC'] %}
        TRY_TO_TIMESTAMP_NTZ(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''))
            AS {{ adapter.quote(col.name) }}
        {% elif name in ['IS_CURRENT'] %}
        TRY_TO_BOOLEAN(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''))
            AS {{ adapter.quote(col.name) }}
        {% else %}
        NULLIF(TRIM({{ adapter.quote(col.name) }}), '')
            AS {{ adapter.quote(col.name) }}
        {% endif %}{% if not loop.last %},{% endif %}
{% endfor %}
    FROM {{ source('travel_bronze', 'customer_address') }}

),

deduplicated AS (

    SELECT *
        FROM cleaned
    WHERE ADDRESS_ID IS NOT NULL
    

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY ADDRESS_ID
        ORDER BY
            UPDATED_AT_UTC DESC NULLS LAST,
            ADDRESS_ID
    ) = 1

)

SELECT *
FROM deduplicated
