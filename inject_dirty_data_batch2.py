
import csv
import json
import random
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CLEAN_DATA_DIR = BASE_DIR / "data_clean"
DOCS_DIR = BASE_DIR / "docs"

MANIFEST_PATH = DOCS_DIR / "dirty_data_manifest_batch2.json"
LOCK_PATH = DOCS_DIR / "dirty_data_batch2.lock"

dirty_manifest = []

# ============================================================
# CSV HELPERS
# ============================================================

def read_csv(filename):
    file_path = DATA_DIR / filename

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(filename, rows):
    if not rows:
        raise ValueError(f"Refusing to write empty dataset: {filename}")

    file_path = DATA_DIR / filename
    fieldnames = list(rows[0].keys())

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def record_issue(
    table_name,
    record_id,
    column_name,
    issue_type,
    original_value,
    injected_value,
    description
):
    issue_id = f"DQ2{len(dirty_manifest) + 1:04d}"

    dirty_manifest.append({
        "issue_id": issue_id,
        "table_name": table_name,
        "record_id": str(record_id),
        "column_name": column_name,
        "issue_type": issue_type,
        "original_value": str(original_value),
        "injected_value": str(injected_value),
        "description": description,
        "injected_at_utc": datetime.now(timezone.utc).isoformat()
    })


def select_rows(rows, count, condition=None):
    candidates = [
        row for row in rows
        if condition is None or condition(row)
    ]

    if count > len(candidates):
        raise ValueError(
            f"Requested {count} records, but only "
            f"{len(candidates)} eligible records exist."
        )

    return random.sample(candidates, count)


# ============================================================
# INJECTION 1: EXACT DUPLICATES
# ============================================================

def inject_exact_duplicates(
    filename,
    table_name,
    primary_key,
    duplicate_count
):
    rows = read_csv(filename)

    selected = select_rows(rows, duplicate_count)

    duplicated_rows = [row.copy() for row in selected]

    for row in selected:
        record_issue(
            table_name=table_name,
            record_id=row[primary_key],
            column_name="ALL_COLUMNS",
            issue_type="exact_duplicate",
            original_value="Original row",
            injected_value="Duplicated row",
            description="An exact duplicate record was added."
        )

    rows.extend(duplicated_rows)
    write_csv(filename, rows)

    print(f"{table_name}: added {duplicate_count} exact duplicates")


# ============================================================
# INJECTION 2: BUSINESS DUPLICATES
# ============================================================

def inject_business_duplicates(
    filename,
    table_name,
    duplicate_count
):
    rows = read_csv(filename)

    selected = select_rows(
        rows,
        duplicate_count,
        condition=lambda row: row.get("BOOKING_ID", "") != ""
    )

    existing_ids = {row["BOOKING_ID"] for row in rows}
    duplicated_rows = []

    for original_row in selected:
        duplicate_row = original_row.copy()

        original_id = original_row["BOOKING_ID"]
        new_id = f"{original_id}_DUP2"

        counter = 2
        while new_id in existing_ids:
            new_id = f"{original_id}_DUP2_{counter}"
            counter += 1

        existing_ids.add(new_id)
        duplicate_row["BOOKING_ID"] = new_id
        duplicated_rows.append(duplicate_row)

        record_issue(
            table_name=table_name,
            record_id=new_id,
            column_name="BOOKING_REFERENCE",
            issue_type="business_duplicate",
            original_value=original_row.get("BOOKING_REFERENCE", ""),
            injected_value=original_row.get("BOOKING_REFERENCE", ""),
            description=(
                "A duplicate booking was created with a new BOOKING_ID "
                "but the same BOOKING_REFERENCE."
            )
        )

    rows.extend(duplicated_rows)
    write_csv(filename, rows)

    print(f"{table_name}: added {duplicate_count} business duplicates")


# ============================================================
# INJECTION 3: MISSING VALUES
# ============================================================

def inject_missing_values(
    filename,
    table_name,
    primary_key,
    column_name,
    missing_count
):
    rows = read_csv(filename)

    selected = select_rows(
        rows,
        missing_count,
        condition=lambda row: row.get(column_name, "") != ""
    )

    for row in selected:
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

    print(f"{table_name}: injected {missing_count} missing values")


# ============================================================
# INJECTION 4: INVALID VALUES
# ============================================================

def inject_invalid_values(
    filename,
    table_name,
    primary_key,
    column_name,
    invalid_value,
    invalid_count,
    issue_type,
    description
):
    rows = read_csv(filename)

    selected = select_rows(
        rows,
        invalid_count,
        condition=lambda row: (
            row.get(column_name, "") != ""
            and row[column_name] != str(invalid_value)
        )
    )

    for row in selected:
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
            description=description
        )

    write_csv(filename, rows)

    print(f"{table_name}: injected {invalid_count} invalid values")


# ============================================================
# INJECTION 5: INCONSISTENT FORMATTING
# ============================================================

def inject_inconsistent_formatting(
    filename,
    table_name,
    primary_key,
    column_name,
    formatting_count
):
    rows = read_csv(filename)

    selected = select_rows(
        rows,
        formatting_count,
        condition=lambda row: (
            row.get(column_name, "") != ""
            and row[column_name] == row[column_name].strip()
        )
    )

    for row in selected:
        record_id = row[primary_key]
        original_value = row[column_name]
        new_value = " " + original_value

        row[column_name] = new_value

        record_issue(
            table_name=table_name,
            record_id=record_id,
            column_name=column_name,
            issue_type="inconsistent_formatting",
            original_value=original_value,
            injected_value=new_value,
            description="Leading whitespace was added to the value."
        )

    write_csv(filename, rows)

    print(f"{table_name}: injected {formatting_count} formatting issues")


# ============================================================
# INJECTION 6: BROKEN FOREIGN KEYS
# ============================================================

def inject_broken_foreign_keys(
    filename,
    table_name,
    primary_key,
    foreign_key_column,
    issue_count
):
    rows = read_csv(filename)

    selected = select_rows(
        rows,
        issue_count,
        condition=lambda row: row.get(foreign_key_column, "") != ""
    )

    for row in selected:
        record_id = row[primary_key]
        original_value = row[foreign_key_column]
        broken_value = f"NONEXISTENT_{original_value}"

        row[foreign_key_column] = broken_value

        record_issue(
            table_name=table_name,
            record_id=record_id,
            column_name=foreign_key_column,
            issue_type="broken_foreign_key",
            original_value=original_value,
            injected_value=broken_value,
            description="Foreign key references a nonexistent record."
        )

    write_csv(filename, rows)

    print(f"{table_name}: injected {issue_count} broken foreign keys")


# ============================================================
# INJECTION 7: TEMPORAL ISSUES
# ============================================================

def inject_temporal_issues(
    filename,
    table_name,
    primary_key,
    start_date_column,
    end_date_column,
    issue_count
):
    rows = read_csv(filename)

    selected = select_rows(
        rows,
        issue_count,
        condition=lambda row: (
            row.get(start_date_column, "") != ""
            and row.get(end_date_column, "") != ""
        )
    )

    for row in selected:
        record_id = row[primary_key]
        original_end_date = row[end_date_column]

        start_date = datetime.strptime(
            row[start_date_column],
            "%Y-%m-%d"
        )

        invalid_end_date = start_date - timedelta(
            days=random.randint(1, 30)
        )

        injected_value = invalid_end_date.strftime("%Y-%m-%d")
        row[end_date_column] = injected_value

        record_issue(
            table_name=table_name,
            record_id=record_id,
            column_name=end_date_column,
            issue_type="invalid_date_range",
            original_value=original_end_date,
            injected_value=injected_value,
            description=(
                f"{end_date_column} is earlier than {start_date_column}."
            )
        )

    write_csv(filename, rows)

    print(f"{table_name}: injected {issue_count} temporal issues")


# ============================================================
# INJECTION 8: REFUNDS EXCEED PAYMENT
# ============================================================

def inject_refund_exceeds_payment(
    filename,
    table_name,
    primary_key,
    issue_count
):
    rows = read_csv(filename)

    selected = select_rows(
        rows,
        issue_count,
        condition=lambda row: (
            row.get("REFUND_AMOUNT", "") != ""
            and float(row["REFUND_AMOUNT"]) > 0
        )
    )

    for row in selected:
        record_id = row[primary_key]
        original_value = row["REFUND_AMOUNT"]

        injected_value = round(float(original_value) * 2, 2)
        row["REFUND_AMOUNT"] = str(injected_value)

        record_issue(
            table_name=table_name,
            record_id=record_id,
            column_name="REFUND_AMOUNT",
            issue_type="refund_exceeds_original",
            original_value=original_value,
            injected_value=injected_value,
            description=(
                "Refund amount was doubled to create a financial anomaly. "
                "Validate against the associated payment."
            )
        )

    write_csv(filename, rows)

    print(f"{table_name}: injected {issue_count} refund anomalies")


# ============================================================
# MANIFEST
# ============================================================

def save_manifest():
    manifest_data = {
        "project": "Travel Data Engineering Platform",
        "batch": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_issues": len(dirty_manifest),
        "issues": dirty_manifest
    }

    temp_manifest = MANIFEST_PATH.with_suffix(".tmp")

    with open(temp_manifest, "w", encoding="utf-8") as file:
        json.dump(
            manifest_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    temp_manifest.replace(MANIFEST_PATH)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("TRAVEL DATA - BATCH 2 DIRTY DATA INJECTION")
    print("=" * 60)

    # Safety checks
    if MANIFEST_PATH.exists():
        raise FileExistsError(
            f"Batch 2 manifest already exists: {MANIFEST_PATH}"
        )

    if LOCK_PATH.exists():
        raise FileExistsError(
            f"Batch 2 lock already exists: {LOCK_PATH}"
        )

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    # Batch 1 clean backup must remain untouched
    if not list(CLEAN_DATA_DIR.glob("*.csv")):
        raise FileNotFoundError(
            "Original clean backups are missing. Injection stopped."
        )

    required_files = [
        "bookings.csv",
        "booking_items.csv",
        "customer_profile.csv",
        "vendors.csv",
        "refunds.csv"
    ]

    missing_files = [
        filename for filename in required_files
        if not (DATA_DIR / filename).exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing required files: " + ", ".join(missing_files)
        )

    # Snapshot affected CSV files in memory for rollback
    snapshot_files = [
        "bookings.csv",
        "booking_items.csv",
        "customer_profile.csv",
        "vendors.csv",
        "refunds.csv"
    ]

    snapshots = {
        filename: (DATA_DIR / filename).read_bytes()
        for filename in snapshot_files
    }

    # Create Batch 2 lock
    LOCK_PATH.write_text(
        datetime.now(timezone.utc).isoformat(),
        encoding="utf-8"
    )

    try:
        print("\nStarting injections...\n")

        # 1. Exact duplicates in bookings
        inject_exact_duplicates(
            filename="bookings.csv",
            table_name="BOOKINGS",
            primary_key="BOOKING_ID",
            duplicate_count=15
        )

        # 2. Business duplicates in bookings
        inject_business_duplicates(
            filename="bookings.csv",
            table_name="BOOKINGS",
            duplicate_count=10
        )

        # 3. Missing email values
        inject_missing_values(
            filename="customer_profile.csv",
            table_name="CUSTOMER_PROFILE",
            primary_key="CUSTOMER_ID",
            column_name="EMAIL",
            missing_count=30
        )

        # 4. Negative gross sales
        inject_invalid_values(
            filename="booking_items.csv",
            table_name="BOOKING_ITEMS",
            primary_key="BOOKING_ITEM_ID",
            column_name="GROSS_SALES_AUD",
            invalid_value="-100",
            invalid_count=15,
            issue_type="negative_gross_sales",
            description="Gross sales cannot be negative."
        )

        # 5. Vendor name formatting issues
        inject_inconsistent_formatting(
            filename="vendors.csv",
            table_name="VENDORS",
            primary_key="VENDOR_BK",
            column_name="VENDOR_NAME",
            formatting_count=20
        )

        # 6. Broken booking customer references
        inject_broken_foreign_keys(
            filename="bookings.csv",
            table_name="BOOKINGS",
            primary_key="BOOKING_ID",
            foreign_key_column="CUSTOMER_ID",
            issue_count=10
        )

        # 7. Invalid check-out dates
        inject_temporal_issues(
            filename="booking_items.csv",
            table_name="BOOKING_ITEMS",
            primary_key="BOOKING_ITEM_ID",
            start_date_column="CHECK_IN_DATE",
            end_date_column="CHECK_OUT_DATE",
            issue_count=10
        )

        # 8. Refund financial anomalies
        inject_refund_exceeds_payment(
            filename="refunds.csv",
            table_name="REFUNDS",
            primary_key="REFUND_ID",
            issue_count=10
        )

        # Save manifest only after all injections succeed
        save_manifest()

        print("\n" + "=" * 60)
        print("BATCH 2 INJECTION COMPLETED")
        print("=" * 60)
        print(f"Total issues injected: {len(dirty_manifest)}")
        print(f"Manifest: {MANIFEST_PATH}")

    except Exception:
        print("\nERROR: Batch 2 failed. Attempting rollback...")

        for filename, content in snapshots.items():
            (DATA_DIR / filename).write_bytes(content)

        print("Rollback attempted for all affected CSV files.")
        raise

    finally:
        if LOCK_PATH.exists():
            LOCK_PATH.unlink()


if __name__ == "__main__":
    main()
