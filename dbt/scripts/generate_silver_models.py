
from pathlib import Path

# Run from travel_data_platform/dbt
models_dir = Path("models/silver/staging")

# Table name: (primary key, numeric columns, date columns, timestamp columns)
tables = {
    "booking_status_history": (
        "STATUS_EVENT_ID", [], [],
        ["STATUS_CHANGED_AT_UTC", "UPDATED_AT_UTC"]
    ),
    "categories": (
        "CATEGORY_BK", [], [], []
    ),
    "vendors": (
        "VENDOR_BK", [], [], ["UPDATED_AT_UTC"]
    ),
    "products": (
        "PRODUCT_BK", [], [],
        ["CREATED_AT_UTC", "UPDATED_AT_UTC"]
    ),
    "offers": (
        "OFFER_BK", ["DISCOUNT_AMOUNT"],
        ["START_DATE", "END_DATE"], []
    ),
    "packages": (
        "PACKAGE_BK", [], [],
        ["CREATED_AT_UTC", "UPDATED_AT_UTC"]
    ),
    "customer_profile": (
        "CUSTOMER_ID", [], ["DATE_OF_BIRTH"],
        ["CREATED_AT_UTC", "UPDATED_AT_UTC"]
    ),
    "customer_address": (
        "ADDRESS_ID", [], ["VALID_FROM", "VALID_TO"],
        ["UPDATED_AT_UTC"]
    ),
    "customer_tier_history": (
        "TIER_HISTORY_ID", [], ["START_DATE", "END_DATE"],
        ["UPDATED_AT_UTC"]
    ),
    "customer_status_history": (
        "STATUS_HISTORY_ID", [], ["START_DATE", "END_DATE"],
        ["UPDATED_AT_UTC"]
    ),
    "payments": (
        "PAYMENT_ID", ["PAYMENT_AMOUNT"], [],
        ["PAYMENT_DATE_UTC", "UPDATED_AT_UTC"]
    ),
    "refunds": (
        "REFUND_ID", ["REFUND_AMOUNT"], [],
        ["REFUND_DATE_UTC", "UPDATED_AT_UTC"]
    ),
    "points_ledger": (
        "LEDGER_ID", ["POINTS_AMOUNT"], ["EXPIRY_DATE"],
        ["EVENT_DATE_UTC", "EVENT_DATE_SYD",
         "CREATED_AT_UTC", "UPDATED_AT_UTC"]
    ),
}

for table, (pk, numeric, dates, timestamps) in tables.items():
    path = models_dir / f"stg_{table}.sql"

    # Use source column names from Snowflake at runtime.
    # dbt's Jinja adapter can inspect the Bronze table.
    sql = f"""{{% set source_relation = source('travel_bronze', '{table}') %}}
{{% set columns = adapter.get_columns_in_relation(source_relation) %}}

WITH cleaned AS (

    SELECT
{{% for col in columns %}}
        {{% set name = col.name | upper %}}
        {{% if name in {numeric!r} %}}
        TRY_TO_DECIMAL(NULLIF(TRIM({{{{ adapter.quote(col.name) }}}}), ''), 18, 2)
            AS {{{{ adapter.quote(col.name) }}}}
        {{% elif name in {dates!r} %}}
        TRY_TO_DATE(NULLIF(TRIM({{{{ adapter.quote(col.name) }}}}), ''))
            AS {{{{ adapter.quote(col.name) }}}}
        {{% elif name in {timestamps!r} %}}
        TRY_TO_TIMESTAMP_NTZ(NULLIF(TRIM({{{{ adapter.quote(col.name) }}}}), ''))
            AS {{{{ adapter.quote(col.name) }}}}
        {{% else %}}
        NULLIF(TRIM({{{{ adapter.quote(col.name) }}}}), '')
            AS {{{{ adapter.quote(col.name) }}}}
        {{% endif %}}{{% if not loop.last %}},{{% endif %}}
{{% endfor %}}
    FROM {{{{ source('travel_bronze', '{table}') }}}}

),

deduplicated AS (

    SELECT *
        FROM cleaned
    WHERE {pk} IS NOT NULL
    {"AND " + numeric[0] + " IS NOT NULL" if table in ["payments", "refunds", "points_ledger"] else ""}

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY {pk}
        ORDER BY
            {"UPDATED_AT_UTC DESC NULLS LAST," if "UPDATED_AT_UTC" in timestamps else ""}
            {pk}
    ) = 1

)

SELECT *
FROM deduplicated
"""

    path.write_text(sql, encoding="utf-8")
    print(f"Generated: {path}")

print(f"Done! Generated {len(tables)} Silver models.")
