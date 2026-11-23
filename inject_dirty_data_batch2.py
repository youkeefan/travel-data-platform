import csv
import json
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CLEAN_DIR = BASE_DIR / "data_clean"
DOCS_DIR = BASE_DIR / "docs"

MANIFEST = DOCS_DIR / "dirty_data_manifest_batch2.json"
LOCK = DOCS_DIR / "dirty_data_batch2.lock"

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


# 1. Exact duplicate rows
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


# 2. Business duplicates: same booking reference, different booking ID
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


# 3. Missing email
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


# 4. Negative gross sales
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


# 5. Leading whitespace in vendor names
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


# 6. Broken customer foreign keys
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


# 7. Checkout date before check-in date
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


# 8. Refund greater than linked payment
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


if __name__ == "__main__":
    main()