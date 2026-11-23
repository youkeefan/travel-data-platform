
from pathlib import Path
import boto3

AWS_PROFILE = "travel-ingestion"
BUCKET_NAME = "travel-data-platform-yf"

PROJECT_DIR = Path(__file__).resolve().parents[2]
TEST_DIR = PROJECT_DIR / "data_test"

session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name="ap-southeast-2"
)
s3 = session.client("s3")

csv_files = sorted(
    file_path
    for file_path in TEST_DIR.glob("*_test_001.csv")
    if file_path.name != "bookings_test_001.csv"
)

if len(csv_files) != 14:
    raise ValueError(
        f"Expected 14 test files, found {len(csv_files)}"
    )

for file_path in csv_files:
    # booking_items_test_001.csv -> booking_items
    table_name = file_path.stem.removesuffix("_test_001")

    s3_key = f"raw/{table_name}/{file_path.name}"

    s3.upload_file(
        str(file_path),
        BUCKET_NAME,
        s3_key
    )

    print(f"Uploaded: {s3_key}")

print("All 14 test files uploaded successfully!")
