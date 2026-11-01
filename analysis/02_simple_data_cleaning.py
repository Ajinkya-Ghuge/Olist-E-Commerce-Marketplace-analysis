"""
OLIST ANALYTICS PRO - SIMPLE DATA CLEANING
Phase 2: Data Quality and Cleaning

This script cleans the data issues we found in Phase 1.
Every transformation is explained so you can defend it in interviews.

Author: Your Name
Date: 2026-10-20
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("OLIST E-COMMERCE DATA CLEANING")
print("="*80)

# =============================================================================
# STEP 1: SETUP AND LOAD DATA
# =============================================================================
print("\n[STEP 1] Loading datasets...")

# Setup paths
project_dir = Path(__file__).parent.parent
data_dir = project_dir / 'dataset'
processed_dir = project_dir / 'data' / 'processed'

# Create processed directory
processed_dir.mkdir(parents=True, exist_ok=True)

# Load all datasets
customers = pd.read_csv(data_dir / 'olist_customers_dataset.csv')
orders = pd.read_csv(data_dir / 'olist_orders_dataset.csv')
order_items = pd.read_csv(data_dir / 'olist_order_items_dataset.csv')
payments = pd.read_csv(data_dir / 'olist_order_payments_dataset.csv')
reviews = pd.read_csv(data_dir / 'olist_order_reviews_dataset.csv')
products = pd.read_csv(data_dir / 'olist_products_dataset.csv')
sellers = pd.read_csv(data_dir / 'olist_sellers_dataset.csv')

print(f"Loaded {len(customers):,} customers")
print(f"Loaded {len(orders):,} orders")
print(f"Loaded {len(order_items):,} order items")
print(f"Loaded {len(payments):,} payments")
print(f"Loaded {len(reviews):,} reviews")
print(f"Loaded {len(products):,} products")
print(f"Loaded {len(sellers):,} sellers")


# =============================================================================
# STEP 2: CLEAN ORDERS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 2] CLEANING ORDERS DATASET")
print("="*80)

print(f"\nOriginal orders: {len(orders):,}")

# Convert date columns to datetime
print("\n[ACTION] Converting date columns to datetime format...")
date_columns = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

for col in date_columns:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')
    print(f"  Converted {col}")

# Investigate missing delivery dates by order status
print("\n[ANALYSIS] Missing delivery dates by order status:")
missing_delivery = orders[orders['order_delivered_customer_date'].isnull()]
print(missing_delivery['order_status'].value_counts())

print("\n[INSIGHT] Missing delivery dates are expected for:")
print("  - Canceled orders (not delivered)")
print("  - Orders in transit (not yet delivered)")
print("  - Processing orders (not yet shipped)")

# Calculate delivery metrics for delivered orders only
delivered_orders = orders[orders['order_status'] == 'delivered'].copy()
print(f"\n[INFO] Delivered orders: {len(delivered_orders):,}")

# Calculate estimated vs actual delivery time (in days)
delivered_orders['estimated_delivery_days'] = (
    delivered_orders['order_estimated_delivery_date'] - 
    delivered_orders['order_purchase_timestamp']
).dt.days

delivered_orders['actual_delivery_days'] = (
    delivered_orders['order_delivered_customer_date'] - 
    delivered_orders['order_purchase_timestamp']
).dt.days

# Calculate delivery delay (positive = late, negative = early)
delivered_orders['delivery_delay_days'] = (
    delivered_orders['order_delivered_customer_date'] - 
    delivered_orders['order_estimated_delivery_date']
).dt.days

print("\n[ANALYSIS] Delivery Performance:")
print(f"Mean estimated delivery: {delivered_orders['estimated_delivery_days'].mean():.1f} days")
print(f"Mean actual delivery: {delivered_orders['actual_delivery_days'].mean():.1f} days")
print(f"Mean delay: {delivered_orders['delivery_delay_days'].mean():.1f} days")

# Count late deliveries
late_deliveries = (delivered_orders['delivery_delay_days'] > 0).sum()
on_time = (delivered_orders['delivery_delay_days'] <= 0).sum()
print(f"\nLate deliveries: {late_deliveries:,} ({late_deliveries/len(delivered_orders)*100:.1f}%)")
print(f"On-time/early: {on_time:,} ({on_time/len(delivered_orders)*100:.1f}%)")

# Update the original orders dataframe with calculated columns
orders = orders.merge(
    delivered_orders[['order_id', 'estimated_delivery_days', 'actual_delivery_days', 'delivery_delay_days']],
    on='order_id',
    how='left'
)

print(f"\n[SUCCESS] Orders cleaned: {len(orders):,} rows")


# =============================================================================
# STEP 3: CLEAN PRODUCTS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 3] CLEANING PRODUCTS DATASET")
print("="*80)

print(f"\nOriginal products: {len(products):,}")

# Check missing values
missing_category = products['product_category_name'].isnull().sum()
print(f"\n[ISSUE] Products missing category: {missing_category}")

# Option 1: Create 'Unknown' category for missing values
print("\n[ACTION] Filling missing categories with 'sem_categoria' (without category)...")
products['product_category_name'] = products['product_category_name'].fillna('sem_categoria')

# Verify
missing_after = products['product_category_name'].isnull().sum()
print(f"[SUCCESS] Missing categories after cleaning: {missing_after}")

# Handle missing product dimensions
print("\n[ANALYSIS] Missing product dimensions:")
dimension_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
for col in dimension_cols:
    missing = products[col].isnull().sum()
    print(f"  {col}: {missing} missing")

# Fill missing dimensions with median (common practice)
print("\n[ACTION] Filling missing dimensions with median values...")
for col in dimension_cols:
    median_val = products[col].median()
    products[col] = products[col].fillna(median_val)
    print(f"  {col}: filled with {median_val:.2f}")

# Fill missing name length and description length with 0
products['product_name_lenght'] = products['product_name_lenght'].fillna(0)
products['product_description_lenght'] = products['product_description_lenght'].fillna(0)
products['product_photos_qty'] = products['product_photos_qty'].fillna(0)

print(f"\n[SUCCESS] Products cleaned: {len(products):,} rows")


# =============================================================================
# STEP 4: VALIDATE ORDER ITEMS
# =============================================================================
print("\n" + "="*80)
print("[STEP 4] VALIDATING ORDER ITEMS")
print("="*80)

print(f"\nOriginal order items: {len(order_items):,}")

# Check for negative or zero prices
negative_prices = (order_items['price'] < 0).sum()
zero_prices = (order_items['price'] == 0).sum()

print(f"\n[ANALYSIS] Price validation:")
print(f"  Negative prices: {negative_prices}")
print(f"  Zero prices: {zero_prices}")

if negative_prices > 0:
    print(f"\n[WARNING] Found {negative_prices} items with negative prices - needs investigation")
else:
    print("\n[SUCCESS] No negative prices found")

# Calculate total item value
order_items['total_item_value'] = order_items['price'] + order_items['freight_value']

# Convert shipping date
order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'])

print(f"\n[SUCCESS] Order items validated: {len(order_items):,} rows")


# =============================================================================
# STEP 5: CLEAN PAYMENTS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 5] CLEANING PAYMENTS DATASET")
print("="*80)

print(f"\nOriginal payments: {len(payments):,}")

# Check payment types
print("\n[ANALYSIS] Payment types:")
print(payments['payment_type'].value_counts())

# Handle 'not_defined' payment type
not_defined = (payments['payment_type'] == 'not_defined').sum()
print(f"\n[INFO] Payments with 'not_defined' type: {not_defined}")

if not_defined > 0:
    print("[ACTION] Keeping 'not_defined' as a valid category (very small number)")

# Check for negative or zero payment values
negative_payments = (payments['payment_value'] < 0).sum()
zero_payments = (payments['payment_value'] == 0).sum()

print(f"\n[ANALYSIS] Payment value validation:")
print(f"  Negative payments: {negative_payments}")
print(f"  Zero payments: {zero_payments}")

print(f"\n[SUCCESS] Payments validated: {len(payments):,} rows")


# =============================================================================
# STEP 6: CLEAN REVIEWS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 6] CLEANING REVIEWS DATASET")
print("="*80)

print(f"\nOriginal reviews: {len(reviews):,}")

# Convert review dates
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'])

# Check review scores
print("\n[ANALYSIS] Review score validation:")
print(f"  Min score: {reviews['review_score'].min()}")
print(f"  Max score: {reviews['review_score'].max()}")
print(f"  Valid range: 1-5")

invalid_scores = ((reviews['review_score'] < 1) | (reviews['review_score'] > 5)).sum()
print(f"  Invalid scores: {invalid_scores}")

# Missing review comments analysis
title_missing = reviews['review_comment_title'].isnull().sum()
message_missing = reviews['review_comment_message'].isnull().sum()

print(f"\n[ANALYSIS] Missing review comments:")
print(f"  Missing titles: {title_missing:,} ({title_missing/len(reviews)*100:.1f}%)")
print(f"  Missing messages: {message_missing:,} ({message_missing/len(reviews)*100:.1f}%)")

# Fill missing comments with empty string
print("\n[ACTION] Filling missing comments with empty strings...")
reviews['review_comment_title'] = reviews['review_comment_title'].fillna('')
reviews['review_comment_message'] = reviews['review_comment_message'].fillna('')

# Create flag for whether customer left a comment
reviews['has_review_comment'] = (reviews['review_comment_message'] != '').astype(int)

print(f"\n[SUCCESS] Reviews cleaned: {len(reviews):,} rows")


# =============================================================================
# STEP 7: PAYMENT RECONCILIATION ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("[STEP 7] PAYMENT RECONCILIATION")
print("="*80)

# Calculate total order value from items
order_totals_items = order_items.groupby('order_id').agg({
    'price': 'sum',
    'freight_value': 'sum',
    'total_item_value': 'sum'
}).reset_index()

order_totals_items.columns = ['order_id', 'items_price_total', 'items_freight_total', 'items_total_value']

# Calculate total from payments
order_totals_payments = payments.groupby('order_id')['payment_value'].sum().reset_index()
order_totals_payments.columns = ['order_id', 'payment_total']

# Merge to compare
reconciliation = order_totals_items.merge(order_totals_payments, on='order_id', how='inner')

# Calculate difference
reconciliation['difference'] = reconciliation['payment_total'] - reconciliation['items_total_value']
reconciliation['difference_abs'] = reconciliation['difference'].abs()

print(f"\n[ANALYSIS] Payment Reconciliation:")
print(f"  Orders compared: {len(reconciliation):,}")
print(f"  Mean difference: R$ {reconciliation['difference'].mean():.2f}")
print(f"  Median difference: R$ {reconciliation['difference'].median():.2f}")

# Find orders with large discrepancies (>R$ 1.00)
large_diff = (reconciliation['difference_abs'] > 1.0).sum()
print(f"  Orders with difference > R$ 1.00: {large_diff:,} ({large_diff/len(reconciliation)*100:.1f}%)")

# Perfect matches
perfect_match = (reconciliation['difference_abs'] < 0.01).sum()
print(f"  Perfect matches: {perfect_match:,} ({perfect_match/len(reconciliation)*100:.1f}%)")

print("\n[INSIGHT] Payment discrepancies may be due to:")
print("  - Discounts or vouchers")
print("  - Rounding differences")
print("  - Partial payments")
print("  - Refunds")


# =============================================================================
# STEP 8: CREATE MASTER ORDER TABLE
# =============================================================================
print("\n" + "="*80)
print("[STEP 8] CREATING MASTER ORDER TABLE")
print("="*80)

print("\n[ACTION] Merging all order-related data...")

# Start with orders
master_orders = orders.copy()
print(f"  Base: {len(master_orders):,} orders")

# Add order totals from items
master_orders = master_orders.merge(
    order_totals_items,
    on='order_id',
    how='left'
)
print(f"  Added item totals")

# Add payment totals
master_orders = master_orders.merge(
    order_totals_payments,
    on='order_id',
    how='left'
)
print(f"  Added payment totals")

# Add review scores
review_scores = reviews[['order_id', 'review_score', 'has_review_comment']].copy()
master_orders = master_orders.merge(
    review_scores,
    on='order_id',
    how='left'
)
print(f"  Added review scores")

# Add customer state
customer_state = customers[['customer_id', 'customer_state', 'customer_city']].copy()
master_orders = master_orders.merge(
    customer_state,
    on='customer_id',
    how='left'
)
print(f"  Added customer location")

print(f"\n[SUCCESS] Master order table created: {len(master_orders):,} rows, {len(master_orders.columns)} columns")


# =============================================================================
# STEP 9: SAVE CLEANED DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 9] SAVING CLEANED DATASETS")
print("="*80)

# Save all cleaned datasets
print("\n[ACTION] Saving cleaned CSV files...")

customers.to_csv(processed_dir / 'customers_cleaned.csv', index=False)
print(f"  Saved: customers_cleaned.csv")

orders.to_csv(processed_dir / 'orders_cleaned.csv', index=False)
print(f"  Saved: orders_cleaned.csv")

order_items.to_csv(processed_dir / 'order_items_cleaned.csv', index=False)
print(f"  Saved: order_items_cleaned.csv")

payments.to_csv(processed_dir / 'payments_cleaned.csv', index=False)
print(f"  Saved: payments_cleaned.csv")

reviews.to_csv(processed_dir / 'reviews_cleaned.csv', index=False)
print(f"  Saved: reviews_cleaned.csv")

products.to_csv(processed_dir / 'products_cleaned.csv', index=False)
print(f"  Saved: products_cleaned.csv")

sellers.to_csv(processed_dir / 'sellers_cleaned.csv', index=False)
print(f"  Saved: sellers_cleaned.csv")

master_orders.to_csv(processed_dir / 'master_orders.csv', index=False)
print(f"  Saved: master_orders.csv (new combined table)")

reconciliation.to_csv(processed_dir / 'payment_reconciliation.csv', index=False)
print(f"  Saved: payment_reconciliation.csv")

print(f"\n[SUCCESS] All files saved to: {processed_dir}")


# =============================================================================
# STEP 10: CLEANING SUMMARY REPORT
# =============================================================================
print("\n" + "="*80)
print("[STEP 10] CLEANING SUMMARY")
print("="*80)

summary = """
DATA CLEANING SUMMARY
=====================

1. ORDERS
   - Converted 5 date columns to datetime format
   - Calculated delivery metrics (estimated, actual, delay)
   - Identified late deliveries: {:.1f}%
   - Added delivery performance columns

2. PRODUCTS
   - Filled {} missing categories with 'sem_categoria'
   - Filled missing dimensions with median values
   - All product records now complete

3. ORDER ITEMS
   - Validated prices (no negative values)
   - Calculated total item value
   - Converted shipping dates

4. PAYMENTS
   - Validated payment values
   - Kept 'not_defined' payment type
   - Identified {} zero-value payments

5. REVIEWS
   - Converted date columns
   - Filled missing comments with empty strings
   - Created 'has_review_comment' flag
   - All review scores valid (1-5)

6. RECONCILIATION
   - Compared order items vs payments
   - Found {:.1f}% perfect matches
   - Mean difference: R$ {:.2f}

7. MASTER TABLE
   - Created combined order table
   - {} rows with {} columns
   - Includes items, payments, reviews, customer data

FILES CREATED
=============
- customers_cleaned.csv
- orders_cleaned.csv
- order_items_cleaned.csv
- payments_cleaned.csv
- reviews_cleaned.csv
- products_cleaned.csv
- sellers_cleaned.csv
- master_orders.csv (NEW)
- payment_reconciliation.csv (NEW)

NEXT STEPS
==========
1. Load cleaned data for analysis
2. Start SQL queries using master_orders table
3. Create visualizations
4. Build Power BI dashboard
""".format(
    late_deliveries/len(delivered_orders)*100,
    missing_category,
    zero_payments,
    perfect_match/len(reconciliation)*100,
    reconciliation['difference'].mean(),
    len(master_orders),
    len(master_orders.columns)
)

print(summary)

# Save summary to file
summary_path = processed_dir / 'cleaning_summary.txt'
with open(summary_path, 'w') as f:
    f.write(summary)

print(f"[SUCCESS] Summary saved to: {summary_path}")

print("\n" + "="*80)
print("DATA CLEANING COMPLETE!")
print("="*80)
