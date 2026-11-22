# ============================================================
# TRAVEL DATA PLATFORM - BATCH 1 DIRTY DATA INJECTION
# ============================================================

import csv
import json
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# 1. CONFIGURATION
# ============================================================

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CLEAN_DATA_DIR = BASE_DIR / "data_clean"
DOCS_DIR = BASE_DIR / "docs"

MANIFEST_PATH = DOCS_DIR / "dirty_data_manifest.json"
LOCK_PATH = DOCS_DIR / "dirty_data_injection.lock"

CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

dirty_manifest = []


# ============================================================
# 2. CSV HELPERS
# ============================================================

def read_csv(filename):
    file_path = DATA_DIR / filename

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(filename, rows):
    if not rows:
        raise ValueError(f"Cannot write empty dataset: {filename}")

    file_path = DATA_DIR / filename
    fieldnames = list(rows[0].keys())

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated: {filename} ({len(rows)} rows)")


def backup_clean_data():
    csv_files = list(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in the data directory."
        )

    existing_backups = list(CLEAN_DATA_DIR.glob("*.csv"))

    if existing_backups:
        raise FileExistsError(
            "Clean backup files already exist. "
            "Backup will not overwrite existing clean data."
        )

    for file_path in csv_files:
        backup_path = CLEAN_DATA_DIR / file_path.name
        shutil.copy2(file_path, backup_path)

        print(f"Backed up: {file_path.name}")

    print(f"Clean backup completed: {len(csv_files)} files")


# ============================================================
# 3. MANIFEST TRACKER
# ============================================================

def record_issue(
    table_name,
    record_id,
    column_name,
    issue_type,
    original_value,
    injected_value,
    description
):
    issue_id = f"DQ{len(dirty_manifest) + 1:04d}"

    issue = {
        "issue_id": issue_id,
        "table_name": table_name,
        "record_id": str(record_id),
        "column_name": column_name,
        "issue_type": issue_type,
        "original_value": str(original_value),
        "injected_value": str(injected_value),
        "description": description,
        "injected_at_utc": datetime.now(timezone.utc).isoformat()
    }

    dirty_manifest.append(issue)

    print(f"Recorded issue: {issue_id} | {table_name} | {issue_type}")


def save_manifest():
    manifest_data = {
        "project": "Travel Data Engineering Platform",
        "batch": "Batch 1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_issues": len(dirty_manifest),
        "issues": dirty_manifest
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as file:
        json.dump(
            manifest_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nManifest saved: {MANIFEST_PATH}")
    print(f"Total recorded issues: {len(dirty_manifest)}")


# ============================================================
# 4. COMMON INJECTION HELPERS
# ============================================================

def get_valid_rows(rows, primary_key):
    return [
        row for row in rows
        if row.get(primary_key, "") != ""
    ]


def select_rows(rows, primary_key, count):
    candidates = get_valid_rows(rows, primary_key)

    if count > len(candidates):
        raise ValueError(
            f"Cannot inject {count} issues. "
            f"Only {len(candidates)} eligible records available."
        )

    return random.sample(candidates, count)


def inject_exact_duplicates(
    filename,
    table_name,
    primary_key,
    duplicate_count
):
    rows = read_csv(filename)

    selected_rows = select_rows(
        rows,
        primary_key,
        duplicate_count
    )

    duplicated_rows = []

    for row in selected_rows:
        duplicated_rows.append(row.copy())

        record_id = row[primary_key]

        record_issue(
            table_name=table_name,
            record_id=record_id,
            column_name="ALL_COLUMNS",
            issue_type="exact_duplicate",
            original_value="Original row",
            injected_value="Duplicated row",
            description="An exact duplicate record was added."
        )

    rows.extend(duplicated_rows)
    write_csv(filename, rows)


def inject_missing_values(
    filename,
    table_name,
    primary_key,
    column_name,
    issue_count
):
    rows = read_csv(filename)

    candidates = [
        row for row in rows
        if row.get(primary_key, "") != ""
        and row.get(column_name, "") != ""
    ]

    selected_rows = select_rows(
        candidates,
        primary_key,
        issue_count
    )

    for row in selected_rows:
        record_id = row[primary_key]
        original_value = row[column_name]

        row[column_name] = ""

        record_issue(
            table_name=table_name,
            record_id=record_id,
            column_name=column_name,
            issue_type="missing_value",
            original_value=original_value,
            injected_value="",
            description=f"Missing value injected into {column_name}."
        )

    write_csv(filename, rows)


def inject_invalid_values(
    filename,
    table_name,
    primary_key,
    column_name,
    invalid_value,
    issue_count,
    issue_type="invalid_value"
):
    rows = read_csv(filename)

    candidates = [
        row for row in rows
        if row.get(primary_key, "") != ""
        and row.get(column_name, "") != ""
    ]

    selected_rows = select_rows(
        candidates,
        primary_key,
        issue_count
    )

    for row in selected_rows:
        record_id = row[primary_key]
        original_value = row[column_name]

        row[column_name] = str(invalid_value)

        record_issue(
            table_name=table_name,
            record_id=record_id,
            column_name=column_name,
            issue_type=issue_type,
            original_value=original_value,
            injected_value=invalid_value,
            description=f"Invalid value injected into {column_name}."
        )

    write_csv(filename, rows)


# ============================================================
# 5. BOOKINGS
# ============================================================

def inject_booking_issues():
    filename = "bookings.csv"
    table_name = "BOOKINGS"
    primary_key = "BOOKING_ID"

    print("\n--- Injecting issues into BOOKINGS ---")

    # Exact duplicates
    inject_exact_duplicates(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        duplicate_count=15
    )

    # Missing customer IDs
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="CUSTOMER_ID",
        issue_count=20
    )

    # Invalid booking status
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="BOOKING_STATUS",
        invalid_value="INVALID_STATUS",
        issue_count=15,
        issue_type="invalid_booking_status"
    )

    # Invalid country code
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="COUNTRY_CODE",
        invalid_value="XX",
        issue_count=10,
        issue_type="invalid_country_code"
    )


# ============================================================
# 6. BOOKING ITEMS
# ============================================================

def inject_booking_item_issues():
    filename = "booking_items.csv"
    table_name = "BOOKING_ITEMS"
    primary_key = "BOOKING_ITEM_ID"

    print("\n--- Injecting issues into BOOKING_ITEMS ---")

    # Exact duplicates
    inject_exact_duplicates(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        duplicate_count=20
    )

    # Missing product references
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="PRODUCT_BK",
        issue_count=20
    )

    # Negative sales values
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="GROSS_SALES_AUD",
        invalid_value="-250.00",
        issue_count=10,
        issue_type="negative_sales"
    )

    # Margin exceeds gross sales
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="GROSS_MARGIN_AUD",
        invalid_value="99999.99",
        issue_count=10,
        issue_type="margin_exceeds_sales"
    )

    # Missing vendor references
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="VENDOR_BK",
        issue_count=15
    )


# ============================================================
# 7. PAYMENTS
# ============================================================

def inject_payment_issues():
    filename = "payments.csv"
    table_name = "PAYMENTS"
    primary_key = "PAYMENT_ID"

    print("\n--- Injecting issues into PAYMENTS ---")

    # Exact duplicates
    inject_exact_duplicates(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        duplicate_count=20
    )

    # Missing transaction references
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="TRANSACTION_REFERENCE",
        issue_count=20
    )

    # Negative payment amounts
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="PAYMENT_AMOUNT",
        invalid_value="-500.00",
        issue_count=10,
        issue_type="negative_payment_amount"
    )

    # Invalid payment status
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="PAYMENT_STATUS",
        invalid_value="INVALID_STATUS",
        issue_count=10,
        issue_type="invalid_payment_status"
    )


# ============================================================
# 8. CUSTOMER PROFILE
# ============================================================

def inject_customer_profile_issues():
    filename = "customer_profile.csv"
    table_name = "CUSTOMER_PROFILE"
    primary_key = "CUSTOMER_ID"

    print("\n--- Injecting issues into CUSTOMER_PROFILE ---")

    # Exact duplicates
    inject_exact_duplicates(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        duplicate_count=15
    )

    # Missing email
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="EMAIL",
        issue_count=30
    )

    # Invalid email format
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="EMAIL",
        invalid_value="not_an_email",
        issue_count=20,
        issue_type="invalid_email_format"
    )

    # Invalid country code
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="COUNTRY_CODE",
        invalid_value="INVALID",
        issue_count=10,
        issue_type="invalid_country_code"
    )


# ============================================================
# 9. CUSTOMER ADDRESS
# ============================================================

def inject_customer_address_issues():
    filename = "customer_address.csv"
    table_name = "CUSTOMER_ADDRESS"
    primary_key = "ADDRESS_ID"

    print("\n--- Injecting issues into CUSTOMER_ADDRESS ---")

    # Exact duplicates
    inject_exact_duplicates(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        duplicate_count=15
    )

    # Missing postcode
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="POSTCODE",
        issue_count=30
    )

    # Invalid country code
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="COUNTRY_CODE",
        invalid_value="ZZ",
        issue_count=10,
        issue_type="invalid_address_country"
    )


# ============================================================
# 10. CUSTOMER TIER HISTORY
# ============================================================

def inject_customer_tier_history_issues():
    filename = "customer_tier_history.csv"
    table_name = "CUSTOMER_TIER_HISTORY"
    primary_key = "TIER_HISTORY_ID"

    print("\n--- Injecting issues into CUSTOMER_TIER_HISTORY ---")

    # Exact duplicates
    inject_exact_duplicates(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        duplicate_count=15
    )

    # Invalid tier
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="TIER_NAME",
        invalid_value="DIAMOND_PLUS",
        issue_count=10,
        issue_type="invalid_tier"
    )

    # Missing customer IDs
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="CUSTOMER_ID",
        issue_count=10
    )


# ============================================================
# 11. CUSTOMER STATUS HISTORY
# ============================================================

def inject_customer_status_history_issues():
    filename = "customer_status_history.csv"
    table_name = "CUSTOMER_STATUS_HISTORY"
    primary_key = "STATUS_HISTORY_ID"

    print("\n--- Injecting issues into CUSTOMER_STATUS_HISTORY ---")

    # Exact duplicates
    inject_exact_duplicates(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        duplicate_count=15
    )

    # Invalid status
    inject_invalid_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="CUSTOMER_STATUS",
        invalid_value="UNKNOWN_STATUS",
        issue_count=10,
        issue_type="invalid_customer_status"
    )

    # Missing customer IDs
    inject_missing_values(
        filename=filename,
        table_name=table_name,
        primary_key=primary_key,
        column_name="CUSTOMER_ID",
        issue_count=10
    )


# ============================================================
# 12. MAIN EXECUTION
# ============================================================

def main():

    print("=" * 60)
    print("TRAVEL DATA - BATCH 1 DIRTY DATA INJECTION")
    print("=" * 60)

    # Prevent accidental re-execution
    if LOCK_PATH.exists() or MANIFEST_PATH.exists():
        raise FileExistsError(
            "A manifest or injection lock already exists. "
            "Injection stopped to prevent accidental re-execution."
        )

    # Check all required source files before modifying anything
    required_files = [
        "bookings.csv",
        "booking_items.csv",
        "payments.csv",
        "customer_profile.csv",
        "customer_address.csv",
        "customer_tier_history.csv",
        "customer_status_history.csv"
    ]

    missing_files = [
        filename for filename in required_files
        if not (DATA_DIR / filename).exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing required CSV files: "
            + ", ".join(missing_files)
        )

    # Create clean backup
    print("\nCreating clean data backup...")
    backup_clean_data()

    # Create lock
    LOCK_PATH.write_text(
        datetime.now(timezone.utc).isoformat(),
        encoding="utf-8"
    )

    print("\nInjection lock created.")

    # --------------------------------------------------------
    # INJECT ISSUES
    # --------------------------------------------------------

    inject_booking_issues()

    inject_booking_item_issues()

    inject_payment_issues()

    inject_customer_profile_issues()

    inject_customer_address_issues()

    inject_customer_tier_history_issues()

    inject_customer_status_history_issues()

    # --------------------------------------------------------
    # SAVE MANIFEST
    # --------------------------------------------------------

    save_manifest()

    print("\n" + "=" * 60)
    print("BATCH 1 DIRTY DATA INJECTION COMPLETED")
    print("=" * 60)

    print(f"Total injected issues: {len(dirty_manifest)}")
    print(f"Clean backup directory: {CLEAN_DATA_DIR}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Lock file: {LOCK_PATH}")


if __name__ == "__main__":
    main()