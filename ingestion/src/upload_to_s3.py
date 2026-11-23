
from pathlib import Path

import boto3

# AWS configuration
AWS_PROFILE = "travel-ingestion"
BUCKET_NAME = "travel-data-platform-yf"
S3_PREFIX = "raw/"

# Locate the CSV data folder
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

# Create an S3 client using your AWS profile
session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name="ap-southeast-2"
)
s3 = session.client("s3")


def upload_csv_files():
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return

    print(f"Found {len(csv_files)} CSV files.")

    for file_path in csv_files:
        s3_key = f"{S3_PREFIX}{file_path.name}"

        try:
            s3.upload_file(
                str(file_path),
                BUCKET_NAME,
                s3_key
            )
            print(f"Uploaded: {file_path.name}")

        except Exception as error:
            print(f"Failed: {file_path.name} - {error}")
            raise

    print("All CSV files uploaded successfully!")


if __name__ == "__main__":
    upload_csv_files()
