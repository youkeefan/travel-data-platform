# ============================================================
# Travel Data Platform - Synthetic Data Generator
# ============================================================

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Reproducibility: same random seed = same dataset every run
random.seed(42)

# Define the directory where generated CSV files will be stored
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Create the data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

print(f"Data output directory: {DATA_DIR}")

def write_csv(filename, rows, fieldnames):
    """
    Write a list of dictionaries to a CSV file.
    """

    file_path = DATA_DIR / filename

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated: {filename} ({len(rows)} rows)")


# ============================================================
# 1. CATEGORIES
# ============================================================

categories = [
    {"CATEGORY_BK": "CAT001", "CATEGORY_NAME": "Hotels", "CATEGORY_GROUP": "Accommodation"},
    {"CATEGORY_BK": "CAT002", "CATEGORY_NAME": "Packages", "CATEGORY_GROUP": "Holiday Packages"},
    {"CATEGORY_BK": "CAT003", "CATEGORY_NAME": "Experiences", "CATEGORY_GROUP": "Activities"},
    {"CATEGORY_BK": "CAT004", "CATEGORY_NAME": "Flights", "CATEGORY_GROUP": "Transport"},
    {"CATEGORY_BK": "CAT005", "CATEGORY_NAME": "Cruises", "CATEGORY_GROUP": "Transport"},
    {"CATEGORY_BK": "CAT006", "CATEGORY_NAME": "Car Hire", "CATEGORY_GROUP": "Transport"},
    {"CATEGORY_BK": "CAT007", "CATEGORY_NAME": "Insurance", "CATEGORY_GROUP": "Other"},
    {"CATEGORY_BK": "CAT008", "CATEGORY_NAME": "Transfers", "CATEGORY_GROUP": "Transport"},
]

write_csv(
    filename="categories.csv",
    rows=categories,
    fieldnames=["CATEGORY_BK", "CATEGORY_NAME", "CATEGORY_GROUP"]
)

# ============================================================
# 2. VENDORS
# ============================================================

vendor_prefixes = [
    "Southern", "Pacific", "Global", "Premier", "Golden",
    "Blue", "Elite", "Royal", "Sunrise", "Ocean"
]

vendor_types = [
    "Travel", "Hotels", "Tours", "Airways", "Resorts",
    "Holiday", "Cruises", "Adventures"
]

vendor_countries = [
    "AU", "NZ", "SG", "JP", "TH", "US", "GB", "FR"
]

vendors = []

for i in range(1, 81):
    vendor_name = (
        f"{random.choice(vendor_prefixes)} "
        f"{random.choice(vendor_types)} {i:03d}"
    )

    vendors.append({
        "VENDOR_BK": f"VEN{i:03d}",
        "VENDOR_NAME": vendor_name,
        "VENDOR_COUNTRY": random.choice(vendor_countries),
        "VENDOR_STATUS": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE"]),
        "UPDATED_AT_UTC": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

write_csv(
    filename="vendors.csv",
    rows=vendors,
    fieldnames=[
        "VENDOR_BK",
        "VENDOR_NAME",
        "VENDOR_COUNTRY",
        "VENDOR_STATUS",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 3. PRODUCTS
# ============================================================

destinations = [
    "Melbourne", "Sydney", "Brisbane", "Perth", "Adelaide",
    "Gold Coast", "Cairns", "Hobart", "Auckland", "Queenstown",
    "Tokyo", "Osaka", "Singapore", "Bangkok", "Bali",
    "Fiji", "London", "Paris", "Rome", "New York"
]

product_statuses = ["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE"]

products = []

for i in range(1, 301):

    # Randomly select an existing category and vendor
    category = random.choice(categories)
    vendor = random.choice(vendors)

    created_at = datetime.now() - timedelta(days=random.randint(30, 1000))

    products.append({
        "PRODUCT_BK": f"PRD{i:04d}",
        "PRODUCT_NAME": f"{random.choice(destinations)} {category['CATEGORY_NAME']} {i:03d}",
        "CATEGORY_BK": category["CATEGORY_BK"],
        "VENDOR_BK": vendor["VENDOR_BK"],
        "DESTINATION": random.choice(destinations),
        "PRODUCT_STATUS": random.choice(product_statuses),
        "CREATED_AT_UTC": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "UPDATED_AT_UTC": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

write_csv(
    filename="products.csv",
    rows=products,
    fieldnames=[
        "PRODUCT_BK",
        "PRODUCT_NAME",
        "CATEGORY_BK",
        "VENDOR_BK",
        "DESTINATION",
        "PRODUCT_STATUS",
        "CREATED_AT_UTC",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 4. OFFERS
# ============================================================

offer_types = [
    "PERCENTAGE",
    "FIXED_AMOUNT",
    "POINTS_MULTIPLIER",
    "FREE_UPGRADE"
]

offers = []

for i in range(1, 51):

    start_date = datetime.now() - timedelta(days=random.randint(0, 365))
    end_date = start_date + timedelta(days=random.randint(7, 90))

    offers.append({
        "OFFER_BK": f"OFR{i:03d}",
        "OFFER_NAME": f"{random.choice(['Summer', 'Winter', 'Member', 'Flash', 'Early Bird'])} Offer {i:03d}",
        "OFFER_TYPE": random.choice(offer_types),
        "DISCOUNT_AMOUNT": round(random.uniform(20, 300), 2),
        "START_DATE": start_date.strftime("%Y-%m-%d"),
        "END_DATE": end_date.strftime("%Y-%m-%d"),
        "OFFER_STATUS": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE"])
    })

write_csv(
    filename="offers.csv",
    rows=offers,
    fieldnames=[
        "OFFER_BK",
        "OFFER_NAME",
        "OFFER_TYPE",
        "DISCOUNT_AMOUNT",
        "START_DATE",
        "END_DATE",
        "OFFER_STATUS"
    ]
)

# ============================================================
# 5. PACKAGES
# ============================================================

package_types = [
    "HOTEL_AND_FLIGHT",
    "HOTEL_AND_EXPERIENCE",
    "ALL_INCLUSIVE",
    "MULTI_CITY",
    "CRUISE_PACKAGE"
]

package_names = [
    "Escape", "Adventure", "Luxury Retreat", "Explorer",
    "Weekend Getaway", "Ultimate Holiday", "Island Experience"
]

packages = []

for i in range(1, 101):

    created_at = datetime.now() - timedelta(days=random.randint(30, 1000))

    packages.append({
        "PACKAGE_BK": f"PKG{i:03d}",
        "PACKAGE_NAME": f"{random.choice(package_names)} {i:03d}",
        "PACKAGE_TYPE": random.choice(package_types),
        "CREATED_AT_UTC": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "UPDATED_AT_UTC": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

write_csv(
    filename="packages.csv",
    rows=packages,
    fieldnames=[
        "PACKAGE_BK",
        "PACKAGE_NAME",
        "PACKAGE_TYPE",
        "CREATED_AT_UTC",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 6. CUSTOMER_PROFILE
# ============================================================

first_names = [
    "Oliver", "Charlotte", "Jack", "Amelia", "Noah",
    "Isla", "William", "Mia", "Lucas", "Ava",
    "Henry", "Grace", "Leo", "Chloe", "Ethan",
    "Sophie", "James", "Emily", "Alexander", "Ella",
    "Liam", "Olivia", "Thomas", "Lily", "Benjamin"
]

last_names = [
    "Smith", "Brown", "Wilson", "Taylor", "Johnson",
    "Lee", "Martin", "Anderson", "Thompson", "White",
    "Walker", "Hall", "Young", "King", "Wright",
    "Scott", "Green", "Baker", "Adams", "Nelson"
]

customer_countries = ["AU", "AU", "AU", "NZ", "SG", "GB", "US"]

genders = ["Female", "Male", "Other", None]

customers = []

for i in range(1, 1501):

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    # Generate a random date of birth for customers aged 18–80
    age = random.randint(18, 80)
    date_of_birth = datetime.now() - timedelta(days=age * 365)

    # Generate a customer creation date within the last 5 years
    created_at = datetime.now() - timedelta(days=random.randint(1, 1825))

    customers.append({
        "CUSTOMER_ID": f"CUST{i:05d}",
        "FIRST_NAME": first_name,
        "LAST_NAME": last_name,
        "EMAIL": f"{first_name.lower()}.{last_name.lower()}.{i}@example.com",
        "PHONE": f"+61{random.randint(400000000, 499999999)}",
        "DATE_OF_BIRTH": date_of_birth.strftime("%Y-%m-%d"),
        "GENDER": random.choice(genders),
        "COUNTRY_CODE": random.choice(customer_countries),
        "CREATED_AT_UTC": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "UPDATED_AT_UTC": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

write_csv(
    filename="customer_profile.csv",
    rows=customers,
    fieldnames=[
        "CUSTOMER_ID",
        "FIRST_NAME",
        "LAST_NAME",
        "EMAIL",
        "PHONE",
        "DATE_OF_BIRTH",
        "GENDER",
        "COUNTRY_CODE",
        "CREATED_AT_UTC",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 7. CUSTOMER_ADDRESS
# ============================================================

cities = {
    "Melbourne": ("VIC", ["3000", "3001", "3051", "3121"]),
    "Sydney": ("NSW", ["2000", "2001", "2010", "2150"]),
    "Brisbane": ("QLD", ["4000", "4001", "4101", "4217"]),
    "Perth": ("WA", ["6000", "6001", "6100", "6150"]),
    "Adelaide": ("SA", ["5000", "5001", "5067", "5081"]),
    "Hobart": ("TAS", ["7000", "7001", "7010", "7050"]),
    "Auckland": ("NZ", ["1010", "1023", "1051", "1071"]),
    "Singapore": ("SG", ["018956", "049318", "238801", "569933"])
}

street_names = [
    "Collins Street", "George Street", "Queen Street",
    "Elizabeth Street", "King Street", "Market Street",
    "Flinders Street", "Victoria Street", "Church Street",
    "High Street", "Station Road", "Main Street"
]

addresses = []

address_id = 1

# The first 500 customers will have 2 address records.
# The remaining 1,000 customers will have 1 address record.
for customer_index, customer in enumerate(customers):

    number_of_addresses = 2 if customer_index < 500 else 1

    # Generate address history
    address_dates = []

    if number_of_addresses == 2:
        current_start = datetime.now() - timedelta(days=random.randint(30, 730))
        historical_start = current_start - timedelta(days=random.randint(365, 1500))

        address_dates = [
            (historical_start, current_start),
            (current_start, None)
        ]
    else:
        current_start = datetime.now() - timedelta(days=random.randint(30, 1825))
        address_dates = [(current_start, None)]

    # Select a city for the customer's current address
    current_city = random.choice(list(cities.keys()))

    # Historical address may be in a different city
    historical_city = random.choice(list(cities.keys()))

    for version_index, (valid_from, valid_to) in enumerate(address_dates):

        # Historical version uses historical city
        if version_index == 0 and number_of_addresses == 2:
            city = historical_city
        else:
            city = current_city

        state, postcodes = cities[city]
        postcode = random.choice(postcodes)

        addresses.append({
            "ADDRESS_ID": f"ADDR{address_id:05d}",
            "CUSTOMER_ID": customer["CUSTOMER_ID"],
            "ADDRESS_LINE_1": f"{random.randint(1, 200)} {random.choice(street_names)}",
            "CITY": city,
            "STATE": state,
            "POSTCODE": postcode,
            "COUNTRY_CODE": customer["COUNTRY_CODE"],
            "VALID_FROM": valid_from.strftime("%Y-%m-%d"),
            "VALID_TO": valid_to.strftime("%Y-%m-%d") if valid_to else None,
            "IS_CURRENT": valid_to is None,
            "UPDATED_AT_UTC": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        address_id += 1

write_csv(
    filename="customer_address.csv",
    rows=addresses,
    fieldnames=[
        "ADDRESS_ID",
        "CUSTOMER_ID",
        "ADDRESS_LINE_1",
        "CITY",
        "STATE",
        "POSTCODE",
        "COUNTRY_CODE",
        "VALID_FROM",
        "VALID_TO",
        "IS_CURRENT",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 8. CUSTOMER_TIER_HISTORY
# ============================================================

tiers = ["Bronze", "Silver", "Gold", "Platinum"]
tier_weights = [50, 30, 15, 5]

tier_history = []
tier_history_id = 1

for customer_index, customer in enumerate(customers):

    # 1,000 customers will have 2 tier records.
    # 500 customers will have 1 tier record.
    number_of_tiers = 2 if customer_index < 1000 else 1

    current_tier = random.choices(
        tiers,
        weights=tier_weights,
        k=1
    )[0]

    if number_of_tiers == 2:

        previous_tier = random.choice(
            [tier for tier in tiers if tier != current_tier]
        )

        current_start = datetime.now() - timedelta(days=random.randint(30, 365))

        historical_start = current_start - timedelta(days=random.randint(180, 1000))

        tier_periods = [
            (previous_tier, historical_start, current_start),
            (current_tier, current_start, None)
        ]

    else:

        current_start = datetime.now() - timedelta(days=random.randint(30, 1825))

        tier_periods = [
            (current_tier, current_start, None)
        ]

    for tier, start_date, end_date in tier_periods:

        tier_history.append({
            "TIER_HISTORY_ID": f"TH{tier_history_id:05d}",
            "CUSTOMER_ID": customer["CUSTOMER_ID"],
            "TIER_NAME": tier,
            "START_DATE": start_date.strftime("%Y-%m-%d"),
            "END_DATE": end_date.strftime("%Y-%m-%d") if end_date else None,
            "IS_CURRENT": end_date is None,
            "UPDATED_AT_UTC": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        tier_history_id += 1

write_csv(
    filename="customer_tier_history.csv",
    rows=tier_history,
    fieldnames=[
        "TIER_HISTORY_ID",
        "CUSTOMER_ID",
        "TIER_NAME",
        "START_DATE",
        "END_DATE",
        "IS_CURRENT",
        "UPDATED_AT_UTC"
    ]
)
# ============================================================
# 9. CUSTOMER_STATUS_HISTORY
# ============================================================

customer_statuses = ["Active", "Inactive", "Suspended"]
status_weights = [85, 12, 3]

status_history = []
status_history_id = 1

for customer_index, customer in enumerate(customers):

    # 500 customers will have 2 status records.
    # 1,000 customers will have 1 status record.
    number_of_statuses = 2 if customer_index < 500 else 1

    current_status = random.choices(
        customer_statuses,
        weights=status_weights,
        k=1
    )[0]

    if number_of_statuses == 2:

        historical_status = random.choice(
            [status for status in customer_statuses if status != current_status]
        )

        current_start = datetime.now() - timedelta(days=random.randint(30, 365))
        historical_start = current_start - timedelta(days=random.randint(180, 1000))

        status_periods = [
            (historical_status, historical_start, current_start),
            (current_status, current_start, None)
        ]

    else:

        current_start = datetime.now() - timedelta(days=random.randint(30, 1825))

        status_periods = [
            (current_status, current_start, None)
        ]

    for status, start_date, end_date in status_periods:

        status_history.append({
            "STATUS_HISTORY_ID": f"SH{status_history_id:05d}",
            "CUSTOMER_ID": customer["CUSTOMER_ID"],
            "CUSTOMER_STATUS": status,
            "START_DATE": start_date.strftime("%Y-%m-%d"),
            "END_DATE": end_date.strftime("%Y-%m-%d") if end_date else None,
            "IS_CURRENT": end_date is None,
            "UPDATED_AT_UTC": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        status_history_id += 1

write_csv(
    filename="customer_status_history.csv",
    rows=status_history,
    fieldnames=[
        "STATUS_HISTORY_ID",
        "CUSTOMER_ID",
        "CUSTOMER_STATUS",
        "START_DATE",
        "END_DATE",
        "IS_CURRENT",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 10. BOOKINGS
# ============================================================

utc_timezone = ZoneInfo("UTC")
sydney_timezone = ZoneInfo("Australia/Sydney")

bookings = []

booking_statuses = ["Confirmed", "Completed", "Cancelled"]
booking_status_weights = [70, 20, 10]

channels = ["Web", "App", "CallCentre"]
channel_weights = [55, 30, 15]

countries = ["AU", "NZ", "SG", "UK"]
country_weights = [75, 10, 8, 7]

currency_mapping = {
    "AU": "AUD",
    "NZ": "NZD",
    "SG": "SGD",
    "UK": "GBP"
}

booking_id = 1

for _ in range(3000):

    customer = random.choice(customers)

    booking_created_at_utc = (
        datetime.now(utc_timezone)
        - timedelta(days=random.randint(1, 1825))
    )

    booking_created_at_syd = booking_created_at_utc.astimezone(
        sydney_timezone
    )

    booking_status = random.choices(
        booking_statuses,
        weights=booking_status_weights,
        k=1
    )[0]

    channel = random.choices(
        channels,
        weights=channel_weights,
        k=1
    )[0]

    country_code = random.choices(
        countries,
        weights=country_weights,
        k=1
    )[0]

    bookings.append({
        "BOOKING_ID": f"B{booking_id:06d}",
        "BOOKING_REFERENCE": f"TRV{booking_id:08d}",
        "CUSTOMER_ID": customer["CUSTOMER_ID"],
        "BOOKING_CREATED_AT_UTC": booking_created_at_utc.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "BOOKING_CREATED_AT_SYD": booking_created_at_syd.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "BOOKING_STATUS": booking_status,
        "CHANNEL": channel,
        "COUNTRY_CODE": country_code,
        "CURRENCY_CODE": currency_mapping[country_code],
        "UPDATED_AT_UTC": datetime.now(utc_timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })

    booking_id += 1

write_csv(
    filename="bookings.csv",
    rows=bookings,
    fieldnames=[
        "BOOKING_ID",
        "BOOKING_REFERENCE",
        "CUSTOMER_ID",
        "BOOKING_CREATED_AT_UTC",
        "BOOKING_CREATED_AT_SYD",
        "BOOKING_STATUS",
        "CHANNEL",
        "COUNTRY_CODE",
        "CURRENCY_CODE",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 11. BOOKING_ITEMS
# ============================================================

category_margin_ranges = {
    "Hotels": (0.15, 0.25),
    "Packages": (0.12, 0.22),
    "Experiences": (0.20, 0.35),
    "Flights": (0.03, 0.10),
    "Cruises": (0.10, 0.20),
}

default_margin_range = (0.10, 0.25)

category_weights = {
    "CAT001": 40,  # Hotels
    "CAT002": 20,  # Packages
    "CAT003": 20,  # Experiences
    "CAT004": 15,  # Flights
    "CAT005": 5,   # Cruises
}

category_name_mapping = {
    category["CATEGORY_BK"]: category["CATEGORY_NAME"]
    for category in categories
}

products_by_category = {}

for product in products:
    category_bk = product["CATEGORY_BK"]
    products_by_category.setdefault(category_bk, []).append(product)

booking_items = []
booking_item_id = 1

for booking_index, booking in enumerate(bookings):

    # First 1,500 bookings have 1 item.
    # Remaining 1,500 bookings have 2 items.
    number_of_items = 1 if booking_index < 1500 else 2

    booking_created_at_utc = datetime.strptime(
        booking["BOOKING_CREATED_AT_UTC"],
        "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=utc_timezone)

    for _ in range(number_of_items):

        category_bk = random.choices(
            list(category_weights.keys()),
            weights=list(category_weights.values()),
            k=1
        )[0]

        product = random.choice(products_by_category[category_bk])
        category_name = category_name_mapping[category_bk]

        margin_range = category_margin_ranges.get(
            category_name,
            default_margin_range
        )

        gross_sales = round(random.uniform(100, 5000), 2)

        margin_pct = random.uniform(
            margin_range[0],
            margin_range[1]
        )

        gross_margin = round(gross_sales * margin_pct, 2)

        discount = round(
            gross_sales * random.uniform(0, 0.15),
            2
        )

        transaction_date_utc = booking_created_at_utc
        transaction_date_syd = transaction_date_utc.astimezone(
            sydney_timezone
        )

        check_in_date = (
            booking_created_at_utc.date()
            + timedelta(days=random.randint(1, 365))
        )

        room_nights = None
        check_out_date = None

        if category_name in ["Hotels", "Packages", "Cruises"]:
            room_nights = random.randint(1, 14)
            check_out_date = check_in_date + timedelta(days=room_nights)

        offer = random.choice(offers) if random.random() < 0.30 else None

        package = (
            random.choice(packages)
            if category_name == "Packages"
            else None
        )

        booking_items.append({
            "BOOKING_ITEM_ID": f"BI{booking_item_id:07d}",
            "BOOKING_ID": booking["BOOKING_ID"],
            "TRANSACTION_DATE_UTC": transaction_date_utc.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "TRANSACTION_DATE_SYD": transaction_date_syd.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "CATEGORY_BK": category_bk,
            "PRODUCT_BK": product["PRODUCT_BK"],
            "VENDOR_BK": product["VENDOR_BK"],
            "GROSS_SALES_AUD": gross_sales,
            "GROSS_MARGIN_AUD": gross_margin,
            "DISCOUNT_AUD": discount,
            "REFUND_AUD": 0.00,
            "OFFER_BK": offer["OFFER_BK"] if offer else None,
            "PACKAGE_BK": package["PACKAGE_BK"] if package else None,
            "CHECK_IN_DATE": (
                check_in_date.strftime("%Y-%m-%d")
                if room_nights is not None else None
            ),
            "CHECK_OUT_DATE": (
                check_out_date.strftime("%Y-%m-%d")
                if check_out_date is not None else None
            ),
            "ROOM_NIGHTS": room_nights,
            "TRAVELLER_COUNT": random.randint(1, 6),
            "UPDATED_AT_UTC": datetime.now(utc_timezone).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        booking_item_id += 1

write_csv(
    filename="booking_items.csv",
    rows=booking_items,
    fieldnames=[
        "BOOKING_ITEM_ID",
        "BOOKING_ID",
        "TRANSACTION_DATE_UTC",
        "TRANSACTION_DATE_SYD",
        "CATEGORY_BK",
        "PRODUCT_BK",
        "VENDOR_BK",
        "GROSS_SALES_AUD",
        "GROSS_MARGIN_AUD",
        "DISCOUNT_AUD",
        "REFUND_AUD",
        "OFFER_BK",
        "PACKAGE_BK",
        "CHECK_IN_DATE",
        "CHECK_OUT_DATE",
        "ROOM_NIGHTS",
        "TRAVELLER_COUNT",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 12. BOOKING_STATUS_HISTORY
# ============================================================

booking_status_history = []
status_event_id = 1

for booking in bookings:

    booking_created_at = datetime.strptime(
        booking["BOOKING_CREATED_AT_UTC"],
        "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=utc_timezone)

    final_status = booking["BOOKING_STATUS"]

    # Define the status transition.
    if final_status == "Confirmed":
        status_sequence = ["Pending", "Confirmed"]

    elif final_status == "Completed":
        status_sequence = ["Confirmed", "Completed"]

    elif final_status == "Cancelled":
        status_sequence = ["Confirmed", "Cancelled"]

    # First event occurs at booking creation.
    first_event_time = booking_created_at

    # Second event occurs after creation, but never in the future.
    max_days_after_creation = max(
        0,
        (datetime.now(utc_timezone) - booking_created_at).days
    )

    days_after_creation = random.randint(
        0,
        min(max_days_after_creation, 30)
    )

    second_event_time = first_event_time + timedelta(
        days=days_after_creation,
        hours=random.randint(1, 23)
    )

    # Prevent the event timestamp from exceeding the current time.
    if second_event_time > datetime.now(utc_timezone):
        second_event_time = datetime.now(utc_timezone)

    event_times = [
        first_event_time,
        second_event_time
    ]

    for status, event_time in zip(status_sequence, event_times):

        booking_status_history.append({
            "STATUS_EVENT_ID": f"BSE{status_event_id:07d}",
            "BOOKING_ID": booking["BOOKING_ID"],
            "BOOKING_STATUS": status,
            "STATUS_CHANGED_AT_UTC": event_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "SOURCE_SYSTEM": "BOOKING_SYSTEM",
            "UPDATED_AT_UTC": datetime.now(utc_timezone).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        status_event_id += 1

write_csv(
    filename="booking_status_history.csv",
    rows=booking_status_history,
    fieldnames=[
        "STATUS_EVENT_ID",
        "BOOKING_ID",
        "BOOKING_STATUS",
        "STATUS_CHANGED_AT_UTC",
        "SOURCE_SYSTEM",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 13. PAYMENTS
# ============================================================

payment_statuses = ["Successful", "Pending", "Failed"]
payment_status_weights = [92, 3, 5]

payment_methods = [
    "Credit Card",
    "Debit Card",
    "PayPal",
    "Bank Transfer"
]

payment_method_weights = [55, 25, 15, 5]

payments = []
payment_id = 1

# Lookup booking item totals.
booking_totals = {}

for item in booking_items:
    booking_id_key = item["BOOKING_ID"]

    booking_totals.setdefault(booking_id_key, 0)

    booking_totals[booking_id_key] += (
        float(item["GROSS_SALES_AUD"])
        - float(item["DISCOUNT_AUD"])
    )

for booking_index, booking in enumerate(bookings):

    # First 2,000 bookings have 1 payment.
    # Remaining 1,000 bookings have 2 payments.
    number_of_payments = 1 if booking_index < 2000 else 2

    total_booking_amount = round(
        booking_totals[booking["BOOKING_ID"]],
        2
    )

    if number_of_payments == 1:
        payment_amounts = [total_booking_amount]

    else:
        split_ratio = random.uniform(0.40, 0.60)

        first_payment = round(
            total_booking_amount * split_ratio,
            2
        )

        second_payment = round(
            total_booking_amount - first_payment,
            2
        )

        payment_amounts = [
            first_payment,
            second_payment
        ]

    booking_created_at_utc = datetime.strptime(
        booking["BOOKING_CREATED_AT_UTC"],
        "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=utc_timezone)

    for payment_amount in payment_amounts:

        payment_date_utc = (
            booking_created_at_utc
            + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23)
            )
        )

        payment_status = random.choices(
            payment_statuses,
            weights=payment_status_weights,
            k=1
        )[0]

        payment_method = random.choices(
            payment_methods,
            weights=payment_method_weights,
            k=1
        )[0]

        payments.append({
            "PAYMENT_ID": f"PAY{payment_id:07d}",
            "BOOKING_ID": booking["BOOKING_ID"],
            "PAYMENT_DATE_UTC": payment_date_utc.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "PAYMENT_AMOUNT": payment_amount,
            "CURRENCY_CODE": booking["CURRENCY_CODE"],
            "PAYMENT_METHOD": payment_method,
            "PAYMENT_STATUS": payment_status,
            "TRANSACTION_REFERENCE": f"TXN{payment_id:010d}",
            "UPDATED_AT_UTC": datetime.now(utc_timezone).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        payment_id += 1

write_csv(
    filename="payments.csv",
    rows=payments,
    fieldnames=[
        "PAYMENT_ID",
        "BOOKING_ID",
        "PAYMENT_DATE_UTC",
        "PAYMENT_AMOUNT",
        "CURRENCY_CODE",
        "PAYMENT_METHOD",
        "PAYMENT_STATUS",
        "TRANSACTION_REFERENCE",
        "UPDATED_AT_UTC"
    ]
)

# ============================================================
# 14. REFUNDS
# ============================================================

refund_reasons = [
    "Customer Cancellation",
    "Booking Modification",
    "Service Issue",
    "Price Adjustment",
    "Duplicate Payment"
]

refund_statuses = ["Completed", "Pending", "Failed"]
refund_status_weights = [85, 10, 5]

refunds = []
refund_id = 1

# Only successful payments can be refunded in our clean dataset.
successful_payments = [
    payment for payment in payments
    if payment["PAYMENT_STATUS"] == "Successful"
]

# Select 500 unique successful payments for refund events.
selected_payments = random.sample(
    successful_payments,
    500
)

for payment in selected_payments:

    payment_amount = float(payment["PAYMENT_AMOUNT"])

    # 70% partial refunds, 30% full refunds.
    if random.random() < 0.70:
        refund_amount = round(
            payment_amount * random.uniform(0.10, 0.90),
            2
        )
    else:
        refund_amount = payment_amount

    payment_date_utc = datetime.strptime(
        payment["PAYMENT_DATE_UTC"],
        "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=utc_timezone)

    refund_date_utc = payment_date_utc + timedelta(
        days=random.randint(1, 60)
    )

    refund_status = random.choices(
        refund_statuses,
        weights=refund_status_weights,
        k=1
    )[0]

    refund_reason = random.choice(refund_reasons)

    refunds.append({
        "REFUND_ID": f"REF{refund_id:07d}",
        "BOOKING_ID": payment["BOOKING_ID"],
        "PAYMENT_ID": payment["PAYMENT_ID"],
        "REFUND_DATE_UTC": refund_date_utc.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "REFUND_AMOUNT": refund_amount,
        "CURRENCY_CODE": payment["CURRENCY_CODE"],
        "REFUND_REASON": refund_reason,
        "REFUND_STATUS": refund_status,
        "UPDATED_AT_UTC": datetime.now(utc_timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })

    refund_id += 1

write_csv(
    filename="refunds.csv",
    rows=refunds,
    fieldnames=[
        "REFUND_ID",
        "BOOKING_ID",
        "PAYMENT_ID",
        "REFUND_DATE_UTC",
        "REFUND_AMOUNT",
        "CURRENCY_CODE",
        "REFUND_REASON",
        "REFUND_STATUS",
        "UPDATED_AT_UTC"
    ]
)


# ============================================================
# 15. POINTS_LEDGER
# ============================================================

event_types = [
    "EARN",
    "REDEEM",
    "EXPIRE",
    "ADJUSTMENT",
    "REVERSAL"
]

event_type_weights = [65, 20, 8, 5, 2]

adjustment_directions = ["CREDIT", "DEBIT"]

points_ledger = []
ledger_id = 1

# Group booking items by booking ID.
booking_items_by_booking = {}

for item in booking_items:
    booking_items_by_booking.setdefault(
        item["BOOKING_ID"], []
    ).append(item)

# Store original events that can be reversed.
previous_ledger_events = []

for _ in range(8000):

    event_type = random.choices(
        event_types,
        weights=event_type_weights,
        k=1
    )[0]

    # Decide whether this event is linked to a booking.
    booking = random.choice(bookings) if random.random() < 0.70 else None

    booking_item = None

    # If linked to a booking, use that booking's customer.
    if booking is not None:

        customer_id = booking["CUSTOMER_ID"]

        available_items = booking_items_by_booking.get(
            booking["BOOKING_ID"], []
        )

        if available_items and random.random() < 0.60:
            booking_item = random.choice(available_items)

    else:

        customer = random.choice(customers)
        customer_id = customer["CUSTOMER_ID"]

    points_amount = random.randint(50, 5000)

    adjustment_direction = None
    related_ledger_id = None

    # Reversal must reference a previous original event.
    if event_type == "REVERSAL":

        if previous_ledger_events:

            original_event = random.choice(
                previous_ledger_events
            )

            # Keep customer consistent with the original event.
            customer_id = original_event["CUSTOMER_ID"]

            related_ledger_id = original_event["LEDGER_ID"]

            points_amount = original_event["POINTS_AMOUNT"]

            # Reversal must happen after the original event.
            original_event_date = original_event["_EVENT_DATETIME"]

            event_date_utc = original_event_date + timedelta(
                days=random.randint(1, 90)
            )

            # Keep booking/item linkage consistent with original event.
            booking_id_value = original_event["BOOKING_ID"]
            booking_item_id_value = original_event["BOOKING_ITEM_ID"]

        else:

            # Fallback if no original event exists yet.
            event_type = "ADJUSTMENT"

            event_date_utc = (
                datetime.now(utc_timezone)
                - timedelta(days=random.randint(0, 1825))
            )

            booking_id_value = booking["BOOKING_ID"] if booking else None

            booking_item_id_value = (
                booking_item["BOOKING_ITEM_ID"]
                if booking_item else None

            )

    else:

        event_date_utc = (
            datetime.now(utc_timezone)
            - timedelta(days=random.randint(0, 1825))
        )

        booking_id_value = booking["BOOKING_ID"] if booking else None

        booking_item_id_value = (
            booking_item["BOOKING_ITEM_ID"]
            if booking_item else None
        )

    if event_type == "ADJUSTMENT":
        adjustment_direction = random.choice(
            adjustment_directions
        )

    expiry_date = None

    if event_type == "EARN":
        expiry_date = (
            event_date_utc.date()
            + timedelta(days=random.randint(365, 1095))
        )

    source_system = random.choice([
        "LOYALTY_SYSTEM",
        "BOOKING_SYSTEM",
        "CRM_SYSTEM"
    ])

    ledger_event = {
        "LEDGER_ID": f"LD{ledger_id:07d}",
        "SOURCE_LEDGER_ID": f"SRC{ledger_id:010d}",
        "CUSTOMER_ID": customer_id,
        "BOOKING_ID": booking_id_value,
        "BOOKING_ITEM_ID": booking_item_id_value,
        "TRANSACTION_ID": f"PTS{ledger_id:010d}",
        "EVENT_TYPE": event_type,
        "POINTS_AMOUNT": points_amount,
        "ADJUSTMENT_DIRECTION": adjustment_direction,
        "RELATED_LEDGER_ID": related_ledger_id,
        "EVENT_DATE_UTC": event_date_utc.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "EVENT_DATE_SYD": event_date_utc.astimezone(
            sydney_timezone
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "EXPIRY_DATE": (
            expiry_date.strftime("%Y-%m-%d")
            if expiry_date else None
        ),
        "SOURCE_SYSTEM": source_system,
        "CREATED_AT_UTC": datetime.now(utc_timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "UPDATED_AT_UTC": datetime.now(utc_timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    points_ledger.append(ledger_event)

    # Keep internal datetime for reversal logic.
    internal_event = ledger_event.copy()
    internal_event["_EVENT_DATETIME"] = event_date_utc

    # Only non-reversal events can be reversal targets.
    if event_type != "REVERSAL":
        previous_ledger_events.append(internal_event)

    ledger_id += 1

write_csv(
    filename="points_ledger.csv",
    rows=points_ledger,
    fieldnames=[
        "LEDGER_ID",
        "SOURCE_LEDGER_ID",
        "CUSTOMER_ID",
        "BOOKING_ID",
        "BOOKING_ITEM_ID",
        "TRANSACTION_ID",
        "EVENT_TYPE",
        "POINTS_AMOUNT",
        "ADJUSTMENT_DIRECTION",
        "RELATED_LEDGER_ID",
        "EVENT_DATE_UTC",
        "EVENT_DATE_SYD",
        "EXPIRY_DATE",
        "SOURCE_SYSTEM",
        "CREATED_AT_UTC",
        "UPDATED_AT_UTC"
    ]
)
