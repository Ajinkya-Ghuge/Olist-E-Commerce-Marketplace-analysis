"""
OLIST ANALYTICS PRO - SIMPLE DATA PROFILING
Phase 1: Understanding the Data

This script analyzes all Olist e-commerce datasets using Pandas and NumPy.
Each section is clearly commented so you can explain it to recruiters.

Author: Your Name
Date: 2026-10-20
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("OLIST E-COMMERCE DATA PROFILING")
print("="*80)

# =============================================================================
# STEP 1: SETUP PATHS
# =============================================================================
print("\n[STEP 1] Setting up file paths...")

# Get the project directory
project_dir = Path(__file__).parent.parent
data_dir = project_dir / 'dataset'
reports_dir = project_dir / 'reports'

# Create reports folder if it doesn't exist
reports_dir.mkdir(exist_ok=True)

print(f"Data directory: {data_dir}")
print(f"Reports directory: {reports_dir}")


# =============================================================================
# STEP 2: LOAD CUSTOMERS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 2] ANALYZING CUSTOMERS DATASET")
print("="*80)

# Load the CSV file into a DataFrame
customers = pd.read_csv(data_dir / 'olist_customers_dataset.csv')

# Basic information about the dataset
print(f"\nRows: {len(customers):,}")
print(f"Columns: {len(customers.columns)}")
print(f"Column names: {list(customers.columns)}")

# Check for missing values using isnull() and sum()
print("\nMissing values per column:")
print(customers.isnull().sum())

# Check for duplicate rows
duplicates = customers.duplicated().sum()
print(f"\nDuplicate rows: {duplicates}")

# Analyze the customer_id column
print("\n[ANALYSIS] Customer ID Column:")
print(f"Total rows: {len(customers):,}")
print(f"Unique customer_ids: {customers['customer_id'].nunique():,}")
print(f"Is customer_id unique? {customers['customer_id'].nunique() == len(customers)}")

# Analyze customer_unique_id (real customer identifier)
print("\n[ANALYSIS] Customer Unique ID Column:")
print(f"Unique customer_unique_ids: {customers['customer_unique_id'].nunique():,}")
repeat_customers = len(customers) - customers['customer_unique_id'].nunique()
print(f"Repeat customers: {repeat_customers:,}")

# Customer location distribution
print("\n[ANALYSIS] Top 10 States by Customer Count:")
state_counts = customers['customer_state'].value_counts().head(10)
print(state_counts)


# =============================================================================
# STEP 3: LOAD ORDERS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 3] ANALYZING ORDERS DATASET")
print("="*80)

# Load orders data
orders = pd.read_csv(data_dir / 'olist_orders_dataset.csv')

print(f"\nRows: {len(orders):,}")
print(f"Columns: {len(orders.columns)}")

# Missing values
print("\nMissing values per column:")
missing = orders.isnull().sum()
print(missing[missing > 0])  # Only show columns with missing values

# Order status distribution
print("\n[ANALYSIS] Order Status Distribution:")
status_counts = orders['order_status'].value_counts()
for status, count in status_counts.items():
    pct = (count / len(orders)) * 100
    print(f"  {status}: {count:,} ({pct:.1f}%)")

# Check if order_id is unique
print(f"\n[ANALYSIS] Unique order_ids: {orders['order_id'].nunique():,}")
print(f"Is order_id unique? {orders['order_id'].nunique() == len(orders)}")

# Convert date columns to datetime
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'], errors='coerce')
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

# Date range analysis
print("\n[ANALYSIS] Order Date Range:")
print(f"First order: {orders['order_purchase_timestamp'].min().date()}")
print(f"Last order: {orders['order_purchase_timestamp'].max().date()}")
print(f"Total days: {(orders['order_purchase_timestamp'].max() - orders['order_purchase_timestamp'].min()).days}")


# =============================================================================
# STEP 4: LOAD ORDER ITEMS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 4] ANALYZING ORDER ITEMS DATASET")
print("="*80)

# Load order items
order_items = pd.read_csv(data_dir / 'olist_order_items_dataset.csv')

print(f"\nRows: {len(order_items):,}")
print(f"Columns: {len(order_items.columns)}")

# Basic statistics for price and freight
print("\n[ANALYSIS] Price Statistics:")
print(f"Mean price: R$ {order_items['price'].mean():.2f}")
print(f"Median price: R$ {order_items['price'].median():.2f}")
print(f"Min price: R$ {order_items['price'].min():.2f}")
print(f"Max price: R$ {order_items['price'].max():.2f}")
print(f"Total GMV: R$ {order_items['price'].sum():,.2f}")

print("\n[ANALYSIS] Freight Statistics:")
print(f"Mean freight: R$ {order_items['freight_value'].mean():.2f}")
print(f"Median freight: R$ {order_items['freight_value'].median():.2f}")
free_shipping = (order_items['freight_value'] == 0).sum()
print(f"Items with free shipping: {free_shipping:,}")

# Items per order analysis
items_per_order = order_items.groupby('order_id').size()
print("\n[ANALYSIS] Items Per Order:")
print(f"Average items per order: {items_per_order.mean():.2f}")
print(f"Max items in one order: {items_per_order.max()}")
single_item_orders = (items_per_order == 1).sum()
multi_item_orders = (items_per_order > 1).sum()
print(f"Orders with 1 item: {single_item_orders:,}")
print(f"Orders with 2+ items: {multi_item_orders:,}")


# =============================================================================
# STEP 5: LOAD PAYMENTS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 5] ANALYZING PAYMENTS DATASET")
print("="*80)

# Load payments
payments = pd.read_csv(data_dir / 'olist_order_payments_dataset.csv')

print(f"\nRows: {len(payments):,}")
print(f"Columns: {len(payments.columns)}")

# Payment method distribution
print("\n[ANALYSIS] Payment Methods:")
payment_methods = payments['payment_type'].value_counts()
for method, count in payment_methods.items():
    pct = (count / len(payments)) * 100
    print(f"  {method}: {count:,} ({pct:.1f}%)")

# Payment statistics
print("\n[ANALYSIS] Payment Value Statistics:")
print(f"Mean payment: R$ {payments['payment_value'].mean():.2f}")
print(f"Total payments: R$ {payments['payment_value'].sum():,.2f}")

# Installment analysis
print("\n[ANALYSIS] Installments:")
print(f"Mean installments: {payments['payment_installments'].mean():.1f}")
print(f"Max installments: {payments['payment_installments'].max()}")

# Multi-payment orders
payments_per_order = payments.groupby('order_id').size()
multi_payment = (payments_per_order > 1).sum()
print(f"\nOrders with multiple payments: {multi_payment:,}")


# =============================================================================
# STEP 6: LOAD REVIEWS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 6] ANALYZING REVIEWS DATASET")
print("="*80)

# Load reviews
reviews = pd.read_csv(data_dir / 'olist_order_reviews_dataset.csv')

print(f"\nRows: {len(reviews):,}")
print(f"Columns: {len(reviews.columns)}")

# Review score distribution
print("\n[ANALYSIS] Review Score Distribution:")
score_counts = reviews['review_score'].value_counts().sort_index()
for score, count in score_counts.items():
    pct = (count / len(reviews)) * 100
    print(f"  Score {score}: {count:,} ({pct:.1f}%)")

print(f"\nMean review score: {reviews['review_score'].mean():.2f}")

# Review comments completeness
title_missing = reviews['review_comment_title'].isnull().sum()
message_missing = reviews['review_comment_message'].isnull().sum()
print("\n[ANALYSIS] Review Comments:")
print(f"Reviews with title: {len(reviews) - title_missing:,} ({(len(reviews)-title_missing)/len(reviews)*100:.1f}%)")
print(f"Reviews with message: {len(reviews) - message_missing:,} ({(len(reviews)-message_missing)/len(reviews)*100:.1f}%)")


# =============================================================================
# STEP 7: LOAD PRODUCTS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 7] ANALYZING PRODUCTS DATASET")
print("="*80)

# Load products
products = pd.read_csv(data_dir / 'olist_products_dataset.csv')

print(f"\nRows: {len(products):,}")
print(f"Columns: {len(products.columns)}")

# Missing values
print("\nMissing values:")
missing = products.isnull().sum()
print(missing[missing > 0])

# Category analysis
print(f"\n[ANALYSIS] Total unique categories: {products['product_category_name'].nunique()}")
print("\nTop 10 Product Categories:")
top_categories = products['product_category_name'].value_counts().head(10)
print(top_categories)


# =============================================================================
# STEP 8: LOAD SELLERS DATA
# =============================================================================
print("\n" + "="*80)
print("[STEP 8] ANALYZING SELLERS DATASET")
print("="*80)

# Load sellers
sellers = pd.read_csv(data_dir / 'olist_sellers_dataset.csv')

print(f"\nRows: {len(sellers):,}")
print(f"Columns: {len(sellers.columns)}")

# Seller geographic distribution
print("\n[ANALYSIS] Top 10 States by Seller Count:")
seller_states = sellers['seller_state'].value_counts().head(10)
print(seller_states)


# =============================================================================
# STEP 9: RELATIONSHIP ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("[STEP 9] ANALYZING RELATIONSHIPS BETWEEN DATASETS")
print("="*80)

# Count unique order_ids in each dataset
order_ids_orders = orders['order_id'].nunique()
order_ids_items = order_items['order_id'].nunique()
order_ids_payments = payments['order_id'].nunique()
order_ids_reviews = reviews['order_id'].nunique()

print("\n[ANALYSIS] Unique Order IDs in Each Dataset:")
print(f"Orders: {order_ids_orders:,}")
print(f"Order Items: {order_ids_items:,}")
print(f"Payments: {order_ids_payments:,}")
print(f"Reviews: {order_ids_reviews:,}")

# Check if all order_ids in items exist in orders
items_order_ids = set(order_items['order_id'])
orders_order_ids = set(orders['order_id'])
orphan_items = items_order_ids - orders_order_ids

print(f"\n[ANALYSIS] Referential Integrity:")
print(f"Order items without matching order: {len(orphan_items)}")


# =============================================================================
# STEP 10: SUMMARY REPORT
# =============================================================================
print("\n" + "="*80)
print("[STEP 10] CREATING SUMMARY REPORT")
print("="*80)

# Create a summary DataFrame
summary_data = {
    'Dataset': ['customers', 'orders', 'order_items', 'payments', 'reviews', 'products', 'sellers'],
    'Rows': [
        len(customers),
        len(orders),
        len(order_items),
        len(payments),
        len(reviews),
        len(products),
        len(sellers)
    ],
    'Columns': [
        len(customers.columns),
        len(orders.columns),
        len(order_items.columns),
        len(payments.columns),
        len(reviews.columns),
        len(products.columns),
        len(sellers.columns)
    ],
    'Missing_Values': [
        customers.isnull().sum().sum(),
        orders.isnull().sum().sum(),
        order_items.isnull().sum().sum(),
        payments.isnull().sum().sum(),
        reviews.isnull().sum().sum(),
        products.isnull().sum().sum(),
        sellers.isnull().sum().sum()
    ],
    'Duplicate_Rows': [
        customers.duplicated().sum(),
        orders.duplicated().sum(),
        order_items.duplicated().sum(),
        payments.duplicated().sum(),
        reviews.duplicated().sum(),
        products.duplicated().sum(),
        sellers.duplicated().sum()
    ]
}

summary_df = pd.DataFrame(summary_data)

print("\nDataset Summary:")
print(summary_df.to_string(index=False))

# Save summary to CSV
summary_path = reports_dir / 'simple_profiling_summary.csv'
summary_df.to_csv(summary_path, index=False)
print(f"\n[SUCCESS] Summary saved to: {summary_path}")


# =============================================================================
# STEP 11: KEY FINDINGS
# =============================================================================
print("\n" + "="*80)
print("KEY FINDINGS")
print("="*80)

print("\n1. DATASET OVERVIEW:")
print(f"   - Total orders: {len(orders):,}")
print(f"   - Total customers: {customers['customer_unique_id'].nunique():,}")
print(f"   - Total products: {len(products):,}")
print(f"   - Total sellers: {len(sellers):,}")

print("\n2. BUSINESS METRICS:")
print(f"   - Total GMV: R$ {order_items['price'].sum():,.2f}")
print(f"   - Average order value: R$ {order_items.groupby('order_id')['price'].sum().mean():.2f}")
print(f"   - Average review score: {reviews['review_score'].mean():.2f}")

print("\n3. DATA QUALITY:")
print(f"   - Total missing values: {summary_df['Missing_Values'].sum():,}")
print(f"   - Datasets with duplicates: {(summary_df['Duplicate_Rows'] > 0).sum()}")

print("\n4. CUSTOMER BEHAVIOR:")
print(f"   - Repeat customers: {repeat_customers:,}")
print(f"   - Single-item orders: {single_item_orders:,}")
print(f"   - Multi-item orders: {multi_item_orders:,}")

print("\n" + "="*80)
print("PROFILING COMPLETE!")
print("="*80)
print("\nNext Steps:")
print("  1. Review the summary CSV file")
print("  2. Investigate missing values")
print("  3. Plan data cleaning strategies")
print("  4. Start Phase 2: Data Quality and Cleaning")
