import csv
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

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


if __name__ == "__main__":
    main()