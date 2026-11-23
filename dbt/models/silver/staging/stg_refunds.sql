{% set source_relation = source('travel_bronze', 'refunds') %}
{% set columns = adapter.get_columns_in_relation(source_relation) %}

WITH cleaned AS (

    SELECT
{% for col in columns %}
        {% set name = col.name | upper %}
        {% if name in ['REFUND_AMOUNT'] %}
        TRY_TO_DECIMAL(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''), 18, 2)
            AS {{ adapter.quote(col.name) }}
        {% elif name in [] %}
        TRY_TO_DATE(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''))
            AS {{ adapter.quote(col.name) }}
        {% elif name in ['REFUND_DATE_UTC', 'UPDATED_AT_UTC'] %}
        TRY_TO_TIMESTAMP_NTZ(NULLIF(TRIM({{ adapter.quote(col.name) }}), ''))
            AS {{ adapter.quote(col.name) }}
        {% else %}
        NULLIF(TRIM({{ adapter.quote(col.name) }}), '')
            AS {{ adapter.quote(col.name) }}
        {% endif %}{% if not loop.last %},{% endif %}
{% endfor %}
    FROM {{ source('travel_bronze', 'refunds') }}

),

deduplicated AS (

    SELECT *
        FROM cleaned
    WHERE REFUND_ID IS NOT NULL
    AND REFUND_AMOUNT IS NOT NULL

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY REFUND_ID
        ORDER BY
            UPDATED_AT_UTC DESC NULLS LAST,
            REFUND_ID
    ) = 1

)

SELECT *
FROM deduplicated
