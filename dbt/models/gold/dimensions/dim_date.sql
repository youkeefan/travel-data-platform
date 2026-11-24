{{ config(materialized='table') }}

WITH date_spine AS (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="CAST('2020-01-01' AS DATE)",
        end_date="CAST('2036-01-01' AS DATE)"
    ) }}

),

base AS (

    SELECT CAST(DATE_DAY AS DATE) AS FULL_DATE
    FROM date_spine

),

final AS (

    SELECT
        -- Date key
        TO_NUMBER(TO_CHAR(FULL_DATE, 'YYYYMMDD')) AS DATE_KEY,
        FULL_DATE,

        -- Calendar attributes
        YEAR(FULL_DATE) AS CALENDAR_YEAR,
        QUARTER(FULL_DATE) AS CALENDAR_QUARTER,
        MONTH(FULL_DATE) AS MONTH_NUMBER,
        MONTHNAME(FULL_DATE) AS MONTH_NAME,
        DAY(FULL_DATE) AS DAY_OF_MONTH,
        DAYOFYEAR(FULL_DATE) AS DAY_OF_YEAR,
        DAYNAME(FULL_DATE) AS DAY_NAME,

        -- ISO week attributes
        WEEKISO(FULL_DATE) AS ISO_WEEK,
        YEAROFWEEKISO(FULL_DATE) AS ISO_YEAR,
        DAYOFWEEKISO(FULL_DATE) AS DAY_OF_WEEK,

        -- Reporting labels
        TO_CHAR(FULL_DATE, 'YYYY-MM') AS YEAR_MONTH,
        YEAR(FULL_DATE) || '-Q' ||
            QUARTER(FULL_DATE) AS YEAR_QUARTER,

        -- Australian financial year
        CASE
            WHEN MONTH(FULL_DATE) >= 7
                THEN YEAR(FULL_DATE) + 1
            ELSE YEAR(FULL_DATE)
        END AS FINANCIAL_YEAR,

        QUARTER(DATEADD('month', -6, FULL_DATE))
            AS FINANCIAL_QUARTER,

        -- Business calendar
        DAYOFWEEKISO(FULL_DATE) IN (6, 7) AS IS_WEEKEND,
        DAYOFWEEKISO(FULL_DATE) BETWEEN 1 AND 5 AS IS_WEEKDAY,

        -- Period boundaries
        DATE_TRUNC('month', FULL_DATE) AS MONTH_START_DATE,
        LAST_DAY(FULL_DATE, 'month') AS MONTH_END_DATE,

        DATE_TRUNC('quarter', FULL_DATE) AS QUARTER_START_DATE,
        LAST_DAY(FULL_DATE, 'quarter') AS QUARTER_END_DATE,

        DATE_TRUNC('year', FULL_DATE) AS YEAR_START_DATE,
        LAST_DAY(FULL_DATE, 'year') AS YEAR_END_DATE

    FROM base

)

SELECT *
FROM final