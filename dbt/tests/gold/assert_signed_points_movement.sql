WITH silver AS (

    SELECT *
    FROM {{ ref('stg_points_ledger') }}

),

expected AS (

    SELECT
        l.LEDGER_ID,

        CASE
            WHEN l.EVENT_TYPE = 'EARN'
                THEN l.POINTS_AMOUNT

            WHEN l.EVENT_TYPE IN ('REDEEM', 'EXPIRE')
                THEN -l.POINTS_AMOUNT

            WHEN l.EVENT_TYPE = 'ADJUSTMENT'
                AND l.ADJUSTMENT_DIRECTION = 'CREDIT'
                THEN l.POINTS_AMOUNT

            WHEN l.EVENT_TYPE = 'ADJUSTMENT'
                AND l.ADJUSTMENT_DIRECTION = 'DEBIT'
                THEN -l.POINTS_AMOUNT

            WHEN l.EVENT_TYPE = 'REVERSAL'
                THEN CASE
                    WHEN o.EVENT_TYPE = 'EARN'
                        THEN -l.POINTS_AMOUNT

                    WHEN o.EVENT_TYPE IN ('REDEEM', 'EXPIRE')
                        THEN l.POINTS_AMOUNT

                    WHEN o.EVENT_TYPE = 'ADJUSTMENT'
                        AND o.ADJUSTMENT_DIRECTION = 'CREDIT'
                        THEN -l.POINTS_AMOUNT

                    WHEN o.EVENT_TYPE = 'ADJUSTMENT'
                        AND o.ADJUSTMENT_DIRECTION = 'DEBIT'
                        THEN l.POINTS_AMOUNT
                END

        END AS EXPECTED_SIGNED_MOVEMENT

    FROM silver l

    LEFT JOIN silver o
        ON l.RELATED_LEDGER_ID = o.LEDGER_ID

),

gold AS (

    SELECT
        LEDGER_ID,
        SIGNED_POINTS_MOVEMENT

    FROM {{ ref('fact_points_ledger') }}

)

SELECT
    COALESCE(e.LEDGER_ID, g.LEDGER_ID) AS LEDGER_ID,
    e.EXPECTED_SIGNED_MOVEMENT,
    g.SIGNED_POINTS_MOVEMENT,

    g.SIGNED_POINTS_MOVEMENT
        - e.EXPECTED_SIGNED_MOVEMENT AS MOVEMENT_VARIANCE

FROM expected e

FULL OUTER JOIN gold g
    ON e.LEDGER_ID = g.LEDGER_ID

WHERE e.LEDGER_ID IS NULL
   OR g.LEDGER_ID IS NULL
   OR e.EXPECTED_SIGNED_MOVEMENT
        IS DISTINCT FROM g.SIGNED_POINTS_MOVEMENT