import csv
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MARKER = BASE_DIR / "batch4_done.txt"

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


if __name__ == "__main__":
    main()