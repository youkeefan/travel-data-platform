
import argparse
import os
import subprocess
from pathlib import Path

import snowflake.connector


ROOT_DIR = Path(__file__).resolve().parents[1]

CONTROL_TABLE = "TRAVEL_DB.MONITORING.DBT_REFRESH_CONTROL"
PROCESSED_TABLE = "TRAVEL_DB.MONITORING.DBT_PROCESSED_FILES"
STATUS_VIEW = "TRAVEL_DB.MONITORING.DBT_REFRESH_STATUS"
PENDING_VIEW = "TRAVEL_DB.MONITORING.DBT_UNPROCESSED_FILES"

PIPELINE = "TRAVEL_DBT_PROD"


def connect():
    return snowflake.connector.connect(
        account="DYJXRCH-MB39782",
        user="TRAVEL_PROD_USER",
        role="TRAVEL_PROD_ROLE",
        warehouse="TRAVEL_PROD_WH",
        database="TRAVEL_DB",
        schema="MONITORING",
        private_key_file=os.environ[
            "SNOWFLAKE_PROD_PRIVATE_KEY_PATH"
        ],
        private_key_file_pwd=os.environ[
            "DBT_ENV_SECRET_PROD_PASSPHRASE"
        ],
    )


def update_status(cursor, status, message):
    cursor.execute(
        f"""
        UPDATE {CONTROL_TABLE}
        SET LAST_RUN_AT = CURRENT_TIMESTAMP(),
            LAST_RUN_STATUS = %s,
            LAST_RUN_MESSAGE = %s
        WHERE PIPELINE_NAME = %s
        """,
        (status, message, PIPELINE),
    )


def refresh(force=False):

    with connect() as conn:
        with conn.cursor() as cursor:

            try:
                # 1. Check whether a refresh is required
                cursor.execute(
                    f"""
                    SELECT REFRESH_REQUIRED
                    FROM {STATUS_VIEW}
                    """
                )

                refresh_required = cursor.fetchone()[0]

                # 2. Skip unnecessary builds
                if not refresh_required and not force:
                    update_status(
                        cursor,
                        "SKIPPED",
                        "No new ingestion events detected",
                    )

                    print("No new data. Skipping dbt build.")
                    return

                # 3. Capture pending files before building
                cursor.execute(
                    f"""
                    SELECT
                        TABLE_NAME,
                        FILE_NAME,
                        LAST_LOAD_TIME
                    FROM {PENDING_VIEW}
                    """
                )

                pending_files = cursor.fetchall()

                print(
                    f"Pending ingestion events: "
                    f"{len(pending_files)}"
                )

                update_status(
                    cursor,
                    "RUNNING",
                    "Production dbt build started",
                )

                # 4. Run production dbt build
                subprocess.run(
                    [
                        "dbt",
                        "build",
                        "--profiles-dir",
                        "cd",
                        "--target",
                        "prod",
                    ],
                    cwd=ROOT_DIR / "dbt",
                    check=True,
                )

                # 5. Record successful processing atomically
                cursor.execute("BEGIN")

                for table_name, file_name, load_time in pending_files:
                    cursor.execute(
                        f"""
                        INSERT INTO {PROCESSED_TABLE}
                            (
                                TABLE_NAME,
                                FILE_NAME,
                                LAST_LOAD_TIME
                            )
                        SELECT %s, %s, %s
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM {PROCESSED_TABLE}
                            WHERE TABLE_NAME = %s
                              AND FILE_NAME = %s
                              AND LAST_LOAD_TIME = %s
                        )
                        """,
                        (
                            table_name,
                            file_name,
                            load_time,
                            table_name,
                            file_name,
                            load_time,
                        ),
                    )

                cursor.execute(
                    f"""
                    UPDATE {CONTROL_TABLE}
                    SET LAST_PROCESSED_LOAD_TIME = (
                            SELECT MAX(LAST_LOAD_TIME)
                            FROM {PROCESSED_TABLE}
                        ),
                        LAST_SUCCESSFUL_REFRESH_AT =
                            CURRENT_TIMESTAMP(),
                        LAST_RUN_AT = CURRENT_TIMESTAMP(),
                        LAST_RUN_STATUS = 'SUCCESS',
                        LAST_RUN_MESSAGE = %s
                    WHERE PIPELINE_NAME = %s
                    """,
                    (
                        f"Processed {len(pending_files)} "
                        "ingestion events",
                        PIPELINE,
                    ),
                )

                cursor.execute("COMMIT")

                print("Production dbt refresh completed.")

            except Exception as error:

                conn.rollback()

                update_status(
                    cursor,
                    "FAILED",
                    type(error).__name__,
                )

                print("Production refresh failed.")
                raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--force",
        action="store_true",
        help="Refresh even when no new data is detected",
    )

    args = parser.parse_args()

    refresh(force=args.force)
