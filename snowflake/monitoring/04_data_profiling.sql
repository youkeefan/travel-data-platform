SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION
FROM TRAVEL_DB.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'BRONZE'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

CREATE TABLE IF NOT EXISTS TRAVEL_DB.MONITORING.COLUMN_PROFILE (
    PROFILE_RUN_ID VARCHAR,
    PROFILED_AT TIMESTAMP_NTZ,
    TABLE_NAME VARCHAR,
    COLUMN_NAME VARCHAR,
    TOTAL_ROWS NUMBER,
    NULL_COUNT NUMBER,
    EMPTY_COUNT NUMBER,
    DISTINCT_COUNT NUMBER,
    NULL_PCT FLOAT,
    EMPTY_PCT FLOAT
);

EXECUTE IMMEDIATE $$
DECLARE
    run_id VARCHAR DEFAULT UUID_STRING();
    run_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP();
    sql_stmt VARCHAR;
    table_nm VARCHAR;
    column_nm VARCHAR;

    col_cursor CURSOR FOR
        SELECT TABLE_NAME, COLUMN_NAME
        FROM TRAVEL_DB.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'BRONZE'
        ORDER BY TABLE_NAME, ORDINAL_POSITION;

BEGIN
    FOR rec IN col_cursor DO

        table_nm := rec.TABLE_NAME;
        column_nm := rec.COLUMN_NAME;

        sql_stmt :=
            'INSERT INTO TRAVEL_DB.MONITORING.COLUMN_PROFILE
             SELECT
                 ?, ?, ?, ?,
                 COUNT(*),
                 COUNT(*) - COUNT("' || column_nm || '"),
                 COALESCE(COUNT_IF(TRIM("' || column_nm || '") = ''''), 0),
                 COUNT(DISTINCT "' || column_nm || '"),
                 ROUND(100.0 * (COUNT(*) - COUNT("' || column_nm || '"))
                     / NULLIF(COUNT(*), 0), 2),
                 ROUND(100.0 * COALESCE(COUNT_IF(TRIM("' || column_nm || '") = ''''), 0)
                     / NULLIF(COUNT(*), 0), 2)
             FROM TRAVEL_DB.BRONZE."' || table_nm || '"';

        EXECUTE IMMEDIATE :sql_stmt
            USING (run_id, run_time, table_nm, column_nm);

    END FOR;

    RETURN 'Profiling completed. Run ID: ' || run_id;
END;
$$;

SELECT
    PROFILE_RUN_ID,
    COUNT(*) AS COLUMNS_PROFILED,
    COUNT(DISTINCT TABLE_NAME) AS TABLES_PROFILED
FROM TRAVEL_DB.MONITORING.COLUMN_PROFILE
GROUP BY PROFILE_RUN_ID;


SELECT
    TABLE_NAME,
    COLUMN_NAME,
    TOTAL_ROWS,
    NULL_COUNT,
    EMPTY_COUNT,
    DISTINCT_COUNT,
    NULL_PCT,
    EMPTY_PCT
FROM TRAVEL_DB.MONITORING.COLUMN_PROFILE
WHERE NULL_COUNT > 0
   OR EMPTY_COUNT > 0
ORDER BY NULL_PCT DESC, EMPTY_PCT DESC;

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    TOTAL_ROWS,
    NULL_COUNT,
    DISTINCT_COUNT,
    TOTAL_ROWS - NULL_COUNT - DISTINCT_COUNT
        AS REPEATED_VALUE_COUNT
FROM TRAVEL_DB.MONITORING.COLUMN_PROFILE
WHERE PROFILE_RUN_ID = (
    SELECT PROFILE_RUN_ID
    FROM TRAVEL_DB.MONITORING.COLUMN_PROFILE
    ORDER BY PROFILED_AT DESC
    LIMIT 1
)
AND (
    COLUMN_NAME LIKE '%ID'
    OR COLUMN_NAME LIKE '%BK'
    OR COLUMN_NAME = 'BOOKING_REFERENCE'
)
ORDER BY REPEATED_VALUE_COUNT DESC;

WITH expected_keys AS (
    SELECT COLUMN1 AS TABLE_NAME,
           COLUMN2 AS COLUMN_NAME
    FROM VALUES
        ('BOOKINGS', 'BOOKING_ID'),
        ('BOOKING_ITEMS', 'BOOKING_ITEM_ID'),
        ('BOOKING_STATUS_HISTORY', 'STATUS_EVENT_ID'),
        ('CUSTOMER_PROFILE', 'CUSTOMER_ID'),
        ('CUSTOMER_ADDRESS', 'ADDRESS_ID'),
        ('CUSTOMER_TIER_HISTORY', 'TIER_HISTORY_ID'),
        ('CUSTOMER_STATUS_HISTORY', 'STATUS_HISTORY_ID'),
        ('PAYMENTS', 'PAYMENT_ID'),
        ('REFUNDS', 'REFUND_ID'),
        ('POINTS_LEDGER', 'LEDGER_ID'),
        ('CATEGORIES', 'CATEGORY_BK'),
        ('PRODUCTS', 'PRODUCT_BK'),
        ('VENDORS', 'VENDOR_BK'),
        ('OFFERS', 'OFFER_BK'),
        ('PACKAGES', 'PACKAGE_BK')
)

SELECT
    p.TABLE_NAME,
    p.COLUMN_NAME,
    p.TOTAL_ROWS,
    p.DISTINCT_COUNT,
    p.NULL_COUNT,
    p.TOTAL_ROWS - p.NULL_COUNT - p.DISTINCT_COUNT
        AS DUPLICATE_COUNT
FROM TRAVEL_DB.MONITORING.COLUMN_PROFILE p
INNER JOIN expected_keys k
    ON p.TABLE_NAME = k.TABLE_NAME
    AND p.COLUMN_NAME = k.COLUMN_NAME
WHERE p.PROFILE_RUN_ID = (
    SELECT PROFILE_RUN_ID
    FROM TRAVEL_DB.MONITORING.COLUMN_PROFILE
    ORDER BY PROFILED_AT DESC
    LIMIT 1
)
ORDER BY DUPLICATE_COUNT DESC;

SELECT
    'BRONZE' AS LAYER,
    COUNT(*) AS TOTAL_ROWS,
    COUNT(DISTINCT BOOKING_ID) AS UNIQUE_IDS,
    COUNT(*) - COUNT(BOOKING_ID) AS NULL_IDS,
    COUNT(BOOKING_ID) - COUNT(DISTINCT BOOKING_ID)
        AS DUPLICATE_COUNT
FROM TRAVEL_DB.BRONZE.BOOKINGS

UNION ALL

SELECT
    'SILVER',
    COUNT(*),
    COUNT(DISTINCT BOOKING_ID),
    COUNT(*) - COUNT(BOOKING_ID),
    COUNT(BOOKING_ID) - COUNT(DISTINCT BOOKING_ID)
FROM TRAVEL_DB.SILVER.STG_BOOKINGS;

SELECT
    COUNT(*) AS TOTAL_ROWS,
    COUNT(BOOKING_CREATED_AT_UTC) AS NON_NULL_VALUES,
    COALESCE(COUNT_IF(
        BOOKING_CREATED_AT_UTC IS NOT NULL
        AND TRY_TO_TIMESTAMP_NTZ(BOOKING_CREATED_AT_UTC) IS NULL
    ), 0) AS INVALID_FORMAT_COUNT,
    MIN(TRY_TO_TIMESTAMP_NTZ(BOOKING_CREATED_AT_UTC))
        AS EARLIEST_BOOKING,
    MAX(TRY_TO_TIMESTAMP_NTZ(BOOKING_CREATED_AT_UTC))
        AS LATEST_BOOKING
FROM TRAVEL_DB.BRONZE.BOOKINGS;

CREATE TABLE IF NOT EXISTS TRAVEL_DB.MONITORING.DATA_QUALITY_RULES (
    RULE_ID VARCHAR,
    TABLE_NAME VARCHAR,
    COLUMN_NAME VARCHAR,
    RULE_TYPE VARCHAR,
    EXPECTED_DATA_TYPE VARCHAR,
    SEVERITY VARCHAR,
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    DESCRIPTION VARCHAR
);

MERGE INTO TRAVEL_DB.MONITORING.DATA_QUALITY_RULES t
USING (
    SELECT
        COLUMN1 AS RULE_ID,
        COLUMN2 AS TABLE_NAME,
        COLUMN3 AS COLUMN_NAME,
        COLUMN4 AS RULE_TYPE,
        COLUMN5 AS EXPECTED_DATA_TYPE,
        COLUMN6 AS SEVERITY,
        COLUMN7 AS DESCRIPTION
    FROM VALUES
        ('DQ001', 'BOOKINGS', 'BOOKING_ID',
         'UNIQUE', 'VARCHAR', 'ERROR',
         'Booking ID must be unique'),

        ('DQ002', 'BOOKINGS', 'BOOKING_CREATED_AT_UTC',
         'VALID_FORMAT', 'TIMESTAMP', 'WARNING',
         'Booking timestamp must be parseable'),

        ('DQ003', 'PAYMENTS', 'PAYMENT_AMOUNT',
         'VALID_FORMAT', 'DECIMAL', 'ERROR',
         'Payment amount must be numeric'),

        ('DQ004', 'CUSTOMER_PROFILE', 'CUSTOMER_ID',
         'NOT_NULL', 'VARCHAR', 'ERROR',
         'Customer ID must not be missing'),

        ('DQ005', 'CUSTOMER_PROFILE', 'DATE_OF_BIRTH',
         'VALID_FORMAT', 'DATE', 'WARNING',
         'Date of birth must be parseable')
) s
ON t.RULE_ID = s.RULE_ID

WHEN NOT MATCHED THEN
    INSERT (
        RULE_ID,
        TABLE_NAME,
        COLUMN_NAME,
        RULE_TYPE,
        EXPECTED_DATA_TYPE,
        SEVERITY,
        IS_ACTIVE,
        DESCRIPTION
    )
    VALUES (
        s.RULE_ID,
        s.TABLE_NAME,
        s.COLUMN_NAME,
        s.RULE_TYPE,
        s.EXPECTED_DATA_TYPE,
        s.SEVERITY,
        TRUE,
        s.DESCRIPTION
    );

SELECT *
FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RULES
ORDER BY RULE_ID;

------Date Quality Results Table
CREATE TABLE IF NOT EXISTS TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS (
    RUN_ID VARCHAR,
    CHECKED_AT TIMESTAMP_NTZ,
    RULE_ID VARCHAR,
    TABLE_NAME VARCHAR,
    COLUMN_NAME VARCHAR,
    RULE_TYPE VARCHAR,
    SEVERITY VARCHAR,
    TOTAL_ROWS NUMBER,
    FAILED_COUNT NUMBER,
    FAILURE_PCT FLOAT,
    CHECK_STATUS VARCHAR
);

-----Automated Data Quality Engine
EXECUTE IMMEDIATE $$
DECLARE
    run_id VARCHAR DEFAULT UUID_STRING();
    run_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP();
    sql_stmt VARCHAR;
    check_expr VARCHAR;
    rule_id_val VARCHAR;
    table_nm VARCHAR;
    column_nm VARCHAR;
    rule_type_val VARCHAR;
    expected_type VARCHAR;
    severity_val VARCHAR;
    col_ref VARCHAR;

    rule_cursor CURSOR FOR
        SELECT *
        FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RULES
        WHERE IS_ACTIVE = TRUE
        ORDER BY RULE_ID;

BEGIN
    FOR rec IN rule_cursor DO

        rule_id_val := rec.RULE_ID;
        table_nm := rec.TABLE_NAME;
        column_nm := rec.COLUMN_NAME;
        rule_type_val := rec.RULE_TYPE;
        expected_type := rec.EXPECTED_DATA_TYPE;
        severity_val := rec.SEVERITY;

        col_ref := '"' || column_nm || '"';
        check_expr := NULL;

        IF (rule_type_val = 'UNIQUE') THEN
            check_expr := 'COUNT(' || col_ref ||
                ') - COUNT(DISTINCT ' || col_ref || ')';

        ELSEIF (rule_type_val = 'NOT_NULL') THEN
            check_expr := 'COUNT(*) - COUNT(' || col_ref || ')';

        ELSEIF (rule_type_val = 'VALID_FORMAT') THEN

            IF (expected_type = 'TIMESTAMP') THEN
                check_expr := 'COUNT_IF(' || col_ref ||
                    ' IS NOT NULL AND TRY_TO_TIMESTAMP_NTZ(' ||
                    col_ref || ') IS NULL)';

            ELSEIF (expected_type = 'DATE') THEN
                check_expr := 'COUNT_IF(' || col_ref ||
                    ' IS NOT NULL AND TRY_TO_DATE(' ||
                    col_ref || ') IS NULL)';

            ELSEIF (expected_type = 'DECIMAL') THEN
                check_expr := 'COUNT_IF(' || col_ref ||
                    ' IS NOT NULL AND TRY_TO_DECIMAL(' ||
                    col_ref || ', 38, 6) IS NULL)';
            END IF;

        END IF;

        IF (check_expr IS NOT NULL) THEN

            sql_stmt :=
                'INSERT INTO TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS
                 SELECT
                     ?, ?, ?, ?, ?, ?, ?,
                     TOTAL_ROWS,
                     FAILED_COUNT,
                     ROUND(100.0 * FAILED_COUNT /
                         NULLIF(TOTAL_ROWS, 0), 2),
                     IFF(FAILED_COUNT = 0, ''PASS'', ''FAIL'')
                 FROM (
                     SELECT COUNT(*) AS TOTAL_ROWS,
                     COALESCE(' || check_expr || ', 0) AS FAILED_COUNT
                     FROM TRAVEL_DB.BRONZE."' || table_nm || '"
                 )';

            EXECUTE IMMEDIATE :sql_stmt
                USING (
                    run_id,
                    run_time,
                    rule_id_val,
                    table_nm,
                    column_nm,
                    rule_type_val,
                    severity_val
                );

        END IF;

    END FOR;

    RETURN 'Data quality checks completed. Run ID: ' || run_id;
END;
$$;

SELECT
    RULE_ID,
    TABLE_NAME,
    COLUMN_NAME,
    RULE_TYPE,
    SEVERITY,
    TOTAL_ROWS,
    FAILED_COUNT,
    FAILURE_PCT,
    CHECK_STATUS
FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS
WHERE RUN_ID = (
    SELECT RUN_ID
    FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS
    ORDER BY CHECKED_AT DESC
    LIMIT 1
)
ORDER BY RULE_ID;

MERGE INTO TRAVEL_DB.MONITORING.DATA_QUALITY_RULES t
USING (
    SELECT
        COLUMN1 AS RULE_ID,
        COLUMN2 AS TABLE_NAME,
        COLUMN3 AS COLUMN_NAME
    FROM VALUES
        ('DQ006', 'BOOKING_ITEMS', 'BOOKING_ITEM_ID'),
        ('DQ007', 'BOOKING_STATUS_HISTORY', 'STATUS_EVENT_ID'),
        ('DQ008', 'CUSTOMER_PROFILE', 'CUSTOMER_ID'),
        ('DQ009', 'CUSTOMER_ADDRESS', 'ADDRESS_ID'),
        ('DQ010', 'CUSTOMER_TIER_HISTORY', 'TIER_HISTORY_ID'),
        ('DQ011', 'CUSTOMER_STATUS_HISTORY', 'STATUS_HISTORY_ID'),
        ('DQ012', 'PAYMENTS', 'PAYMENT_ID'),
        ('DQ013', 'REFUNDS', 'REFUND_ID'),
        ('DQ014', 'POINTS_LEDGER', 'LEDGER_ID'),
        ('DQ015', 'CATEGORIES', 'CATEGORY_BK'),
        ('DQ016', 'PRODUCTS', 'PRODUCT_BK'),
        ('DQ017', 'VENDORS', 'VENDOR_BK'),
        ('DQ018', 'OFFERS', 'OFFER_BK'),
        ('DQ019', 'PACKAGES', 'PACKAGE_BK')
) s
ON t.RULE_ID = s.RULE_ID

WHEN NOT MATCHED THEN
    INSERT (
        RULE_ID,
        TABLE_NAME,
        COLUMN_NAME,
        RULE_TYPE,
        EXPECTED_DATA_TYPE,
        SEVERITY,
        IS_ACTIVE,
        DESCRIPTION
    )
    VALUES (
        s.RULE_ID,
        s.TABLE_NAME,
        s.COLUMN_NAME,
        'UNIQUE',
        'VARCHAR',
        'ERROR',
        TRUE,
        'Expected key must be unique'
    );

MERGE INTO TRAVEL_DB.MONITORING.DATA_QUALITY_RULES t
USING (
    SELECT
        COLUMN1 AS RULE_ID,
        COLUMN2 AS TABLE_NAME,
        COLUMN3 AS COLUMN_NAME,
        COLUMN4 AS EXPECTED_DATA_TYPE,
        COLUMN5 AS SEVERITY
    FROM VALUES
        ('DQ020', 'CUSTOMER_ADDRESS', 'VALID_FROM',
         'DATE', 'WARNING'),
        ('DQ021', 'CUSTOMER_TIER_HISTORY', 'START_DATE',
         'DATE', 'WARNING'),
        ('DQ022', 'CUSTOMER_STATUS_HISTORY', 'START_DATE',
         'DATE', 'WARNING'),
        ('DQ023', 'BOOKING_ITEMS', 'GROSS_SALES_AUD',
         'DECIMAL', 'ERROR'),
        ('DQ024', 'BOOKING_ITEMS', 'GROSS_MARGIN_AUD',
         'DECIMAL', 'ERROR'),
        ('DQ025', 'REFUNDS', 'REFUND_AMOUNT',
         'DECIMAL', 'ERROR'),
        ('DQ026', 'POINTS_LEDGER', 'POINTS_AMOUNT',
         'DECIMAL', 'ERROR'),
        ('DQ027', 'BOOKING_ITEMS', 'DISCOUNT_AUD',
         'DECIMAL', 'ERROR'),
        ('DQ028', 'BOOKING_ITEMS', 'REFUND_AUD',
         'DECIMAL', 'ERROR')
) s
ON t.RULE_ID = s.RULE_ID

WHEN NOT MATCHED THEN
    INSERT (
        RULE_ID,
        TABLE_NAME,
        COLUMN_NAME,
        RULE_TYPE,
        EXPECTED_DATA_TYPE,
        SEVERITY,
        IS_ACTIVE,
        DESCRIPTION
    )
    VALUES (
        s.RULE_ID,
        s.TABLE_NAME,
        s.COLUMN_NAME,
        'VALID_FORMAT',
        s.EXPECTED_DATA_TYPE,
        s.SEVERITY,
        TRUE,
        'Value must match expected data type'
    );

SELECT
    RULE_TYPE,
    COUNT(*) AS RULE_COUNT
FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RULES
GROUP BY RULE_TYPE;

INSERT INTO TRAVEL_DB.MONITORING.DATA_QUALITY_RULES
(
    RULE_ID,
    TABLE_NAME,
    COLUMN_NAME,
    RULE_TYPE,
    EXPECTED_DATA_TYPE,
    SEVERITY,
    IS_ACTIVE,
    DESCRIPTION
)
SELECT
    'NN_' || r.RULE_ID,
    r.TABLE_NAME,
    r.COLUMN_NAME,
    'NOT_NULL',
    r.EXPECTED_DATA_TYPE,
    'ERROR',
    TRUE,
    'Expected key must not be NULL'
FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RULES r
WHERE r.RULE_TYPE = 'UNIQUE'
    AND r.IS_ACTIVE = TRUE
    AND NOT EXISTS (
        SELECT 1
        FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RULES n
        WHERE n.TABLE_NAME = r.TABLE_NAME
            AND n.COLUMN_NAME = r.COLUMN_NAME
            AND n.RULE_TYPE = 'NOT_NULL'
    );

SELECT
    RULE_TYPE,
    COUNT(*) AS RULE_COUNT
FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RULES
GROUP BY RULE_TYPE;

SELECT
    RULE_TYPE,
    COUNT(*) AS TOTAL_RULES,
    COUNT_IF(CHECK_STATUS = 'PASS') AS PASSED,
    COUNT_IF(CHECK_STATUS = 'FAIL') AS FAILED
FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS
WHERE RUN_ID = (
    SELECT RUN_ID
    FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS
    ORDER BY CHECKED_AT DESC
    LIMIT 1
)
GROUP BY RULE_TYPE
ORDER BY RULE_TYPE;

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    RULE_TYPE,
    SEVERITY,
    FAILED_COUNT,
    FAILURE_PCT
FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS
WHERE RUN_ID = (
    SELECT RUN_ID
    FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RESULTS
    ORDER BY CHECKED_AT DESC
    LIMIT 1
)
AND CHECK_STATUS = 'FAIL'
ORDER BY FAILED_COUNT DESC;

SELECT
    'INVALID_DATE_RECORDS' AS QUARANTINE_VIEW,
    COUNT(*) AS RECORD_COUNT
FROM TRAVEL_DB.SILVER.INVALID_DATE_RECORDS

UNION ALL

SELECT
    'INVALID_FINANCIAL_RECORDS',
    COUNT(*)
FROM TRAVEL_DB.SILVER.INVALID_FINANCIAL_RECORDS;

EXECUTE IMMEDIATE $$
DECLARE
    sql_stmt VARCHAR DEFAULT '';

    rule_cursor CURSOR FOR
        SELECT TABLE_NAME, COLUMN_NAME
        FROM TRAVEL_DB.MONITORING.DATA_QUALITY_RULES
        WHERE RULE_TYPE = 'UNIQUE'
          AND IS_ACTIVE = TRUE
        ORDER BY TABLE_NAME;

    results RESULTSET;

BEGIN
    FOR rec IN rule_cursor DO

        IF (sql_stmt <> '') THEN
            sql_stmt := sql_stmt || ' UNION ALL ';
        END IF;

        sql_stmt := sql_stmt ||
            'SELECT ''STG_' || rec.TABLE_NAME ||
            ''' AS MODEL_NAME,
            COUNT(*) AS TOTAL_ROWS,
            COUNT(DISTINCT "' || rec.COLUMN_NAME ||
            '") AS UNIQUE_IDS,
            COUNT("' || rec.COLUMN_NAME ||
            '") - COUNT(DISTINCT "' || rec.COLUMN_NAME ||
            '") AS DUPLICATE_COUNT
            FROM TRAVEL_DB.SILVER.STG_' || rec.TABLE_NAME;

    END FOR;

    results := (EXECUTE IMMEDIATE :sql_stmt);

    RETURN TABLE(results);
END;
$$;