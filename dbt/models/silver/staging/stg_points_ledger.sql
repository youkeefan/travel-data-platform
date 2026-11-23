{% set source_relation = source('travel_bronze', 'points_ledger') %}
{% set columns = adapter.get_columns_in_relation(source_relation) %}

WITH cleaned AS (

    SELECT
{% for col in columns %}
        {% set name = col.name | upper %}
        {% if name in ['POINTS_AMOUNT'] %}
        TRY_TO_DECIMAL(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''), 18, 2)
            AS {{ adapter.quote(col.name) }}
        {% elif name in ['EXPIRY_DATE'] %}
        TRY_TO_DATE(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''))
            AS {{ adapter.quote(col.name) }}
        {% elif name in ['EVENT_DATE_UTC', 'EVENT_DATE_SYD', 'CREATED_AT_UTC', 'UPDATED_AT_UTC'] %}
        TRY_TO_TIMESTAMP_NTZ(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''))
            AS {{ adapter.quote(col.name) }}
        {% else %}
        NULLIF(TRIM({{ adapter.quote(col.name) }}), '')
            AS {{ adapter.quote(col.name) }}
        {% endif %}{% if not loop.last %},{% endif %}
{% endfor %}
    FROM {{ source('travel_bronze', 'points_ledger') }}

),

deduplicated AS (

    SELECT *
        FROM cleaned
    WHERE LEDGER_ID IS NOT NULL
    AND POINTS_AMOUNT IS NOT NULL

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY LEDGER_ID
        ORDER BY
            UPDATED_AT_UTC DESC NULLS LAST,
            LEDGER_ID
    ) = 1

)

SELECT *
FROM deduplicated
