
{{ config(materialized='view') }}

WITH invalid_booking_items AS (

    SELECT
        'booking_items' AS SOURCE_TABLE,
        BOOKING_ITEM_ID AS RECORD_ID,
        GROSS_SALES_AUD AS RAW_VALUE,
        'INVALID_GROSS_SALES_AUD' AS ERROR_REASON
    FROM {{ source('travel_bronze', 'booking_items') }}
    WHERE GROSS_SALES_AUD IS NOT NULL
      AND TRY_TO_DECIMAL(GROSS_SALES_AUD, 18, 2) IS NULL

),

invalid_payments AS (

    SELECT
        'payments' AS SOURCE_TABLE,
        PAYMENT_ID AS RECORD_ID,
        PAYMENT_AMOUNT AS RAW_VALUE,
        'INVALID_PAYMENT_AMOUNT' AS ERROR_REASON
    FROM {{ source('travel_bronze', 'payments') }}
    WHERE PAYMENT_AMOUNT IS NOT NULL
      AND TRY_TO_DECIMAL(PAYMENT_AMOUNT, 18, 2) IS NULL

),

invalid_refunds AS (

    SELECT
        'refunds' AS SOURCE_TABLE,
        REFUND_ID AS RECORD_ID,
        REFUND_AMOUNT AS RAW_VALUE,
        'INVALID_REFUND_AMOUNT' AS ERROR_REASON
    FROM {{ source('travel_bronze', 'refunds') }}
    WHERE REFUND_AMOUNT IS NOT NULL
      AND TRY_TO_DECIMAL(REFUND_AMOUNT, 18, 2) IS NULL

),

invalid_points AS (

    SELECT
        'points_ledger' AS SOURCE_TABLE,
        LEDGER_ID AS RECORD_ID,
        POINTS_AMOUNT AS RAW_VALUE,
        'INVALID_POINTS_AMOUNT' AS ERROR_REASON
    FROM {{ source('travel_bronze', 'points_ledger') }}
    WHERE POINTS_AMOUNT IS NOT NULL
      AND TRY_TO_DECIMAL(POINTS_AMOUNT, 18, 2) IS NULL

)

SELECT * FROM invalid_booking_items
UNION ALL
SELECT * FROM invalid_payments
UNION ALL
SELECT * FROM invalid_refunds
UNION ALL
SELECT * FROM invalid_points
