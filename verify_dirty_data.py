import csv
import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CLEAN_DATA_DIR = BASE_DIR / "data_clean"
MANIFEST_PATH = BASE_DIR / "docs" / "dirty_data_manifest.json"


def count_csv_rows(file_path):
    """Count data rows in a CSV file, excluding the header."""
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        return sum(1 for _ in csv.DictReader(file))


def main():
    print("=" * 70)
    print("TRAVEL DATA - DIRTY DATA VERIFICATION")
    print("=" * 70)

    # Load manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    issues = manifest["issues"]
    issue_counts = Counter(
        issue["table_name"] for issue in issues
    )

    print(f"\nManifest issues: {len(issues)}")
    print(f"Manifest total:  {manifest['total_issues']}")

    print("\nIssues by table:")
    for table, count in sorted(issue_counts.items()):
        print(f"  {table:<30} {count:>5}")

    # Compare clean and dirty CSV row counts
    print("\n" + "-" * 70)
    print("ROW COUNT COMPARISON")
    print("-" * 70)

    clean_files = sorted(CLEAN_DATA_DIR.glob("*.csv"))

    print(
        f"{'TABLE':<35}"
        f"{'CLEAN ROWS':>12}"
        f"{'DIRTY ROWS':>12}"
        f"{'DIFFERENCE':>12}"
    )

    for clean_file in clean_files:
        dirty_file = DATA_DIR / clean_file.name

        clean_count = count_csv_rows(clean_file)

        if dirty_file.exists():
            dirty_count = count_csv_rows(dirty_file)
            difference = dirty_count - clean_count
        else:
            dirty_count = 0
            difference = -clean_count

        table_name = clean_file.stem.upper()

        print(
            f"{table_name:<35}"
            f"{clean_count:>12}"
            f"{dirty_count:>12}"
            f"{difference:>12}"
        )

    print("\n" + "=" * 70)
    print("VERIFICATION FINISHED - NO FILES MODIFIED")
    print("=" * 70)


if __name__ == "__main__":
    main()