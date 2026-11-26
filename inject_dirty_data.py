"""Travel Data Platform: consolidated dirty data injection (batches 1–4).
Run only against disposable local CSV data, never already-injected data.
"""
import argparse
import csv
import json
import random
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CLEAN_DIR = BASE_DIR / "data_clean"
DOCS_DIR = BASE_DIR / "docs"
MANIFEST_PATH = DOCS_DIR / "dirty_data_manifest.json"
LOCK_PATH = DOCS_DIR / "dirty_data_injection.lock"
MANIFEST = DOCS_DIR / "dirty_data_manifest_batch2.json"
LOCK = DOCS_DIR / "dirty_data_batch2.lock"
MARKER = BASE_DIR / "batch4_done.txt"


def inject_batch1():
    random.seed(42)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dirty_manifest = []

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

        existing_backups = list(CLEAN_DIR.glob("*.csv"))

        if existing_backups:
            raise FileExistsError(
                "Clean backup files already exist. "
                "Backup will not overwrite existing clean data."
            )

        for file_path in csv_files:
            backup_path = CLEAN_DIR / file_path.name
            shutil.copy2(file_path, backup_path)

            print(f"Backed up: {file_path.name}")

        print(f"Clean backup completed: {len(csv_files)} files")

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
        print(f"Clean backup directory: {CLEAN_DIR}")
        print(f"Manifest: {MANIFEST_PATH}")
        print(f"Lock file: {LOCK_PATH}")

    main()


def inject_batch2():
    random.seed(42)
    issues = []

    def read_csv(filename):
        with open(DATA_DIR / filename, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def write_csv(filename, rows):
        with open(DATA_DIR / filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def log_issue(table, record_id, column, issue_type, original, injected):
        issues.append({
            "issue_id": f"DQ2{len(issues) + 1:04d}",
            "table": table,
            "record_id": str(record_id),
            "column": column,
            "issue_type": issue_type,
            "original_value": str(original),
            "injected_value": str(injected)
        })

    def choose(rows, count, condition=lambda r: True):
        candidates = [r for r in rows if condition(r)]

        if len(candidates) < count:
            raise ValueError(
                f"Not enough eligible rows: need {count}, found {len(candidates)}"
            )

        return random.sample(candidates, count)

    def inject_exact_duplicates():
        filename = "bookings.csv"
        rows = read_csv(filename)

        selected = choose(
            rows, 15,
            lambda r: r.get("BOOKING_ID", "") != ""
        )

        for row in selected:
            log_issue(
                "BOOKINGS", row["BOOKING_ID"], "ALL_COLUMNS",
                "exact_duplicate", "Original row", "Duplicated row"
            )

        rows.extend([r.copy() for r in selected])
        write_csv(filename, rows)

    def inject_business_duplicates():
        filename = "bookings.csv"
        rows = read_csv(filename)

        selected = choose(
            rows, 10,
            lambda r: r.get("BOOKING_ID", "") != ""
        )

        existing_ids = {r["BOOKING_ID"] for r in rows}

        for row in selected:
            duplicate = row.copy()
            original_id = row["BOOKING_ID"]
            new_id = f"{original_id}_DUP2"

            while new_id in existing_ids:
                new_id += "_X"

            existing_ids.add(new_id)
            duplicate["BOOKING_ID"] = new_id

            log_issue(
                "BOOKINGS", new_id, "BOOKING_REFERENCE",
                "business_duplicate",
                row["BOOKING_REFERENCE"],
                duplicate["BOOKING_REFERENCE"]
            )

            rows.append(duplicate)

        write_csv(filename, rows)

    def inject_missing_emails():
        filename = "customer_profile.csv"
        rows = read_csv(filename)

        selected = choose(
            rows, 30,
            lambda r: r.get("EMAIL", "") != ""
        )

        for row in selected:
            original = row["EMAIL"]
            row["EMAIL"] = ""

            log_issue(
                "CUSTOMER_PROFILE", row["CUSTOMER_ID"], "EMAIL",
                "missing_value", original, ""
            )

        write_csv(filename, rows)

    def inject_negative_sales():
        filename = "booking_items.csv"
        rows = read_csv(filename)

        selected = choose(
            rows, 15,
            lambda r: r.get("GROSS_SALES_AUD", "") != ""
        )

        for row in selected:
            original = row["GROSS_SALES_AUD"]
            row["GROSS_SALES_AUD"] = "-100"

            log_issue(
                "BOOKING_ITEMS", row["BOOKING_ITEM_ID"],
                "GROSS_SALES_AUD", "negative_value",
                original, "-100"
            )

        write_csv(filename, rows)

    def inject_vendor_whitespace():
        filename = "vendors.csv"
        rows = read_csv(filename)

        selected = choose(
            rows, 20,
            lambda r: (
                r.get("VENDOR_NAME", "") != ""
                and r["VENDOR_NAME"] == r["VENDOR_NAME"].strip()
            )
        )

        for row in selected:
            original = row["VENDOR_NAME"]
            row["VENDOR_NAME"] = " " + original

            log_issue(
                "VENDORS", row["VENDOR_BK"], "VENDOR_NAME",
                "leading_whitespace", original, row["VENDOR_NAME"]
            )

        write_csv(filename, rows)

    def inject_broken_customer_ids():
        filename = "bookings.csv"
        rows = read_csv(filename)

        selected = choose(
            rows, 10,
            lambda r: r.get("CUSTOMER_ID", "") != ""
        )

        for row in selected:
            original = row["CUSTOMER_ID"]
            row["CUSTOMER_ID"] = "INVALID_" + original

            log_issue(
                "BOOKINGS", row["BOOKING_ID"], "CUSTOMER_ID",
                "broken_foreign_key", original, row["CUSTOMER_ID"]
            )

        write_csv(filename, rows)

    def inject_invalid_checkout_dates():
        filename = "booking_items.csv"
        rows = read_csv(filename)

        def parse_date(value):
            return datetime.strptime(value[:10], "%Y-%m-%d")

        selected = choose(
            rows, 10,
            lambda r: (
                r.get("CHECK_IN_DATE", "") != ""
                and r.get("CHECK_OUT_DATE", "") != ""
            )
        )

        for row in selected:
            original = row["CHECK_OUT_DATE"]
            check_in = parse_date(row["CHECK_IN_DATE"])

            invalid_checkout = check_in - timedelta(days=5)
            injected = invalid_checkout.strftime("%Y-%m-%d")

            row["CHECK_OUT_DATE"] = injected

            log_issue(
                "BOOKING_ITEMS", row["BOOKING_ITEM_ID"],
                "CHECK_OUT_DATE", "invalid_date_range",
                original, injected
            )

        write_csv(filename, rows)

    def inject_refunds_exceeding_payments():
        refunds_file = "refunds.csv"
        payments_file = "payments.csv"

        refunds = read_csv(refunds_file)
        payments = read_csv(payments_file)

        payment_amounts = {}

        for payment in payments:
            payment_id = payment.get("PAYMENT_ID", "")
            amount = payment.get("PAYMENT_AMOUNT", "")

            if payment_id and amount:
                try:
                    amount = float(amount)
                    if amount > 0:
                        payment_amounts[payment_id] = amount
                except ValueError:
                    continue

        candidates = [
            r for r in refunds
            if r.get("PAYMENT_ID", "") in payment_amounts
            and r.get("REFUND_AMOUNT", "") != ""
        ]

        selected = choose(candidates, 10)

        for refund in selected:
            payment_id = refund["PAYMENT_ID"]
            original = refund["REFUND_AMOUNT"]

            payment_amount = payment_amounts[payment_id]
            injected = round(payment_amount + 100, 2)

            refund["REFUND_AMOUNT"] = f"{injected:.2f}"

            log_issue(
                "REFUNDS", refund["REFUND_ID"], "REFUND_AMOUNT",
                "refund_exceeds_payment", original, refund["REFUND_AMOUNT"]
            )

        write_csv(refunds_file, refunds)

    def save_manifest():
        data = {
            "batch": 2,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_issues": len(issues),
            "issues": issues
        }

        temp_file = MANIFEST.with_suffix(".tmp")

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        temp_file.replace(MANIFEST)

    def main():
        if MANIFEST.exists():
            raise FileExistsError("Batch 2 has already been run.")

        if LOCK.exists():
            raise FileExistsError("Batch 2 lock file exists.")

        if not CLEAN_DIR.exists():
            raise FileNotFoundError("data_clean backup is missing.")

        required_files = [
            "bookings.csv",
            "booking_items.csv",
            "customer_profile.csv",
            "vendors.csv",
            "refunds.csv",
            "payments.csv"
        ]

        for filename in required_files:
            if not (DATA_DIR / filename).exists():
                raise FileNotFoundError(f"Missing file: {filename}")

        # Backup the files that Batch 2 will modify, in memory.
        modified_files = [
            "bookings.csv",
            "booking_items.csv",
            "customer_profile.csv",
            "vendors.csv",
            "refunds.csv"
        ]

        backups = {
            filename: (DATA_DIR / filename).read_bytes()
            for filename in modified_files
        }

        with open(LOCK, "x", encoding="utf-8") as f:
            f.write("Batch 2 running")

        try:
            inject_exact_duplicates()
            inject_business_duplicates()
            inject_missing_emails()
            inject_negative_sales()
            inject_vendor_whitespace()
            inject_broken_customer_ids()
            inject_invalid_checkout_dates()
            inject_refunds_exceeding_payments()

            save_manifest()

            print("Batch 2 injection completed!")
            print(f"Total dirty data injected: {len(issues)}")
            print(f"Manifest saved: {MANIFEST}")

        except Exception:
            print("Error detected. Restoring modified CSV files...")

            for filename, content in backups.items():
                (DATA_DIR / filename).write_bytes(content)

            if MANIFEST.exists():
                MANIFEST.unlink()

            print("Rollback completed.")
            raise

        finally:
            if LOCK.exists():
                LOCK.unlink()

    main()


def inject_batch3():
    TARGETS = {
        "bookings.csv": ("BOOKING_ID", "BOOKING_STATUS", "INVALID_STATUS"),
        "booking_items.csv": ("BOOKING_ITEM_ID", "PRODUCT_BK", ""),
        "customer_address.csv": ("ADDRESS_ID", "POSTCODE", ""),
        "customer_profile.csv": ("CUSTOMER_ID", "EMAIL", ""),
        "customer_tier_history.csv": ("TIER_HISTORY_ID", "TIER_NAME", "INVALID_TIER"),
        "payments.csv": ("PAYMENT_ID", "TRANSACTION_REFERENCE", ""),
        "points_ledger.csv": ("LEDGER_ID", "EVENT_TYPE", "INVALID_EVENT"),
        "refunds.csv": ("REFUND_ID", "REFUND_AMOUNT", "-100.00"),
    }

    def main():
        rng = random.Random(42)
        pending = {}

        for filename, (id_col, dirty_col, bad_value) in TARGETS.items():
            path = DATA_DIR / filename

            with path.open(newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                fields = reader.fieldnames
                rows = list(reader)

            if not fields or id_col not in fields or dirty_col not in fields:
                raise ValueError(f"Missing required columns in {filename}")

            candidates = [
                i for i, row in enumerate(rows)
                if row[id_col].strip()
                and row[dirty_col].strip()
                and row[dirty_col] != bad_value
            ]

            if len(candidates) < 10:
                raise ValueError(f"Not enough eligible records in {filename}")

            selected = rng.sample(candidates, 10)

            for i in selected[:5]:
                rows[i][dirty_col] = bad_value

            for i in selected[5:]:
                rows.append(rows[i].copy())

            pending[filename] = (fields, rows)

        for filename, (fields, rows) in pending.items():
            with (DATA_DIR / filename).open(
                "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

            print(f"{filename}: 5 invalid values + 5 duplicate rows")

        print("Done: 80 dirty records injected across 8 CSV files.")

    main()


def inject_batch4():
    TARGETS = {
        "bookings.csv": ("BOOKING_ID", "BOOKING_CREATED_AT_UTC", "not_a_timestamp"),
        "booking_items.csv": ("BOOKING_ITEM_ID", "GROSS_SALES_AUD", "not_a_number"),
        "customer_address.csv": ("ADDRESS_ID", "VALID_FROM", "not_a_date"),
        "customer_profile.csv": ("CUSTOMER_ID", "DATE_OF_BIRTH", "not_a_date"),
        "customer_tier_history.csv": ("TIER_HISTORY_ID", "START_DATE", "not_a_date"),
        "payments.csv": ("PAYMENT_ID", "PAYMENT_AMOUNT", "not_a_number"),
        "points_ledger.csv": ("LEDGER_ID", "POINTS_AMOUNT", "not_a_number"),
        "refunds.csv": ("REFUND_ID", "REFUND_AMOUNT", "not_a_number"),
    }

    def main():
        if MARKER.exists():
            raise RuntimeError("Batch 4 already completed. No files changed.")

        rng = random.Random(44)
        pending = {}

        for filename, (id_column, target_column, bad_value) in TARGETS.items():
            path = DATA_DIR / filename

            with path.open("r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames
                rows = list(reader)

            if not columns or id_column not in columns or target_column not in columns:
                raise ValueError(f"Missing required columns in {filename}")

            eligible = [
                i for i, row in enumerate(rows)
                if row[id_column].strip()
                and row[target_column].strip()
                and row[target_column] != bad_value
            ]

            if len(eligible) < 3:
                raise ValueError(f"Not enough eligible records in {filename}")

            for i in rng.sample(eligible, 3):
                rows[i][target_column] = bad_value

            pending[filename] = (columns, rows)

        for filename, (columns, rows) in pending.items():
            with (DATA_DIR / filename).open(
                "w", newline="", encoding="utf-8"
            ) as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)

            print(f"{filename}: 3 wrong-type values injected")

        MARKER.write_text("Batch 4 completed\n", encoding="utf-8")
        print("Done: 24 existing records modified. Row counts unchanged.")

    main()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, choices=["1", "2", "3", "4", "all"])
    args = parser.parse_args()
    batches = {"1": inject_batch1, "2": inject_batch2, "3": inject_batch3, "4": inject_batch4}
    if args.batch == "all":
        # Preflight known completion markers before touching data.
        for path in (MANIFEST_PATH, LOCK_PATH, MANIFEST, LOCK, MARKER):
            if path.exists():
                parser.error(f"Existing batch marker: {path}. Use a fresh dataset.")
        for run in batches.values():
            run()
    else:
        batches[args.batch]()


if __name__ == "__main__":
    main()
