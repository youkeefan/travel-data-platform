CREATE OR REPLACE SEMANTIC VIEW SEMANTIC.COMMERCIAL_ANALYTICS
	tables (
		COMMERCIAL as GOLD.MART_COMMERCIAL_DAILY primary key (COMMERCIAL_DAILY_KEY) comment='Daily commercial performance at transaction date and product grain. Includes only booking items with positive gross sales.'
	)
	facts (
		COMMERCIAL.SALES_AMOUNT as GROSS_SALES_AUD,
		COMMERCIAL.MARGIN_AMOUNT as GROSS_MARGIN_AUD,
		COMMERCIAL.DISCOUNT_AMOUNT as DISCOUNT_AUD,
		COMMERCIAL.REFUND_AMOUNT as REFUND_AUD,
		COMMERCIAL.ITEM_COUNT as BOOKING_ITEM_COUNT,
		COMMERCIAL.ROOM_NIGHT_COUNT as ROOM_NIGHTS,
		COMMERCIAL.TRAVELLER_COUNT as TRAVELLER_COUNT
	)
	dimensions (
		COMMERCIAL.TRANSACTION_DATE as TRANSACTION_DATE,
		COMMERCIAL.CALENDAR_YEAR as CALENDAR_YEAR,
		COMMERCIAL.CALENDAR_QUARTER as CALENDAR_QUARTER,
		COMMERCIAL.YEAR_MONTH as YEAR_MONTH,
		COMMERCIAL.FINANCIAL_YEAR as FINANCIAL_YEAR,
		COMMERCIAL.FINANCIAL_QUARTER as FINANCIAL_QUARTER,
		COMMERCIAL.PRODUCT_NAME as PRODUCT_NAME,
		COMMERCIAL.DESTINATION as DESTINATION,
		COMMERCIAL.PRODUCT_STATUS as PRODUCT_STATUS,
		COMMERCIAL.CATEGORY_NAME as CATEGORY_NAME,
		COMMERCIAL.CATEGORY_GROUP as CATEGORY_GROUP,
		COMMERCIAL.VENDOR_NAME as VENDOR_NAME,
		COMMERCIAL.VENDOR_COUNTRY as VENDOR_COUNTRY
	)
	metrics (
		COMMERCIAL.TOTAL_SALES as SUM(commercial.sales_amount) with synonyms=('gross sales','total gross sales') comment='Total gross sales in AUD.',
		COMMERCIAL.TOTAL_MARGIN as SUM(commercial.margin_amount) with synonyms=('gross margin','total gross margin') comment='Total gross margin in AUD.',
		COMMERCIAL.TOTAL_DISCOUNT as SUM(commercial.discount_amount),
		COMMERCIAL.TOTAL_REFUND as SUM(commercial.refund_amount),
		COMMERCIAL.TOTAL_BOOKING_ITEMS as SUM(commercial.item_count),
		COMMERCIAL.TOTAL_ROOM_NIGHTS as SUM(commercial.room_night_count),
		COMMERCIAL.TOTAL_TRAVELLERS as SUM(commercial.traveller_count) comment='Sum of item-level traveller counts, not unique travellers.',
		COMMERCIAL.GROSS_MARGIN_RATE as SUM(commercial.margin_amount)
        / NULLIF(SUM(commercial.sales_amount), 0) comment='Weighted gross margin rate expressed as a decimal.',
		COMMERCIAL.AVERAGE_BOOKING_ITEM_VALUE as SUM(commercial.sales_amount)
        / NULLIF(SUM(commercial.item_count), 0) comment='Average gross sales per booking item in AUD.'
	)
	comment='Business semantic layer for travel commercial analytics.';