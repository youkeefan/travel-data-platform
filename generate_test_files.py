
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "data_test"

OUTPUT_DIR.mkdir(exist_ok=True)

# Bookings has already been tested
EXCLUDE = {"bookings.csv"}

for source_file in sorted(SOURCE_DIR.glob("*.csv")):
    if source_file.name in EXCLUDE:
        continue

    with source_file.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        row = next(reader, None)

    if not columns or row is None:
        print(f"Skipped empty file: {source_file.name}")
        continue

    # Copy one existing record for schema compatibility
    test_row = row.copy()

    # Give the record a unique test identifier
    id_columns = [
        "BOOKING_ITEM_ID",
        "CUSTOMER_ID",
        "PAYMENT_ID",
        "REFUND_ID",
        "LEDGER_ID",
        "ADDRESS_ID",
        "TIER_HISTORY_ID",
        "STATUS_HISTORY_ID",
        "STATUS_EVENT_ID",
        "PRODUCT_BK",
        "CATEGORY_BK",
        "VENDOR_BK",
        "OFFER_BK",
        "PACKAGE_BK",
    ]

    for column in id_columns:
        if column in test_row:
            test_row[column] = f"TEST_{column}_001"
            break

    output_file = OUTPUT_DIR / f"{source_file.stem}_test_001.csv"

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerow(test_row)

    print(f"Created: {output_file.name}")

print("Test file generation complete!")
