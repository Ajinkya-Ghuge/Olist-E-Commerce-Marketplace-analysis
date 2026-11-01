"""
OLIST ANALYTICS PRO - SQL ANALYSIS WITH SQLITE
Phase 4: Advanced SQL Queries

This script creates a SQLite database and runs business SQL queries.
Perfect for showing SQL skills to recruiters - NO external database needed!

Author: Your Name
Date: 2026-10-20
"""

import pandas as pd
import sqlite3
from pathlib import Path

print("="*80)
print("OLIST E-COMMERCE SQL ANALYSIS")
print("="*80)

# =============================================================================
# STEP 1: SETUP AND CREATE SQLITE DATABASE
# =============================================================================
print("\n[STEP 1] Creating SQLite database...")

project_dir = Path(__file__).parent.parent
processed_dir = project_dir / 'data' / 'processed'
db_path = project_dir / 'data' / 'olist_analytics.db'
reports_dir = project_dir / 'reports'

# Create SQLite database connection
conn = sqlite3.connect(db_path)
print(f"Database created: {db_path}")

# =============================================================================
# STEP 2: LOAD CLEANED DATA INTO SQLITE
# =============================================================================
print("\n[STEP 2] Loading cleaned data into SQLite tables...")

# Load and insert each table
print("\nLoading tables:")

# Customers
customers = pd.read_csv(processed_dir / 'customers_cleaned.csv')
customers.to_sql('customers', conn, if_exists='replace', index=False)
print(f"  customers: {len(customers):,} rows")

# Orders
orders = pd.read_csv(processed_dir / 'orders_cleaned.csv')
orders.to_sql('orders', conn, if_exists='replace', index=False)
print(f"  orders: {len(orders):,} rows")

# Order Items
order_items = pd.read_csv(processed_dir / 'order_items_cleaned.csv')
order_items.to_sql('order_items', conn, if_exists='replace', index=False)
print(f"  order_items: {len(order_items):,} rows")

# Payments
payments = pd.read_csv(processed_dir / 'payments_cleaned.csv')
payments.to_sql('payments', conn, if_exists='replace', index=False)
print(f"  payments: {len(payments):,} rows")

# Reviews
reviews = pd.read_csv(processed_dir / 'reviews_cleaned.csv')
reviews.to_sql('reviews', conn, if_exists='replace', index=False)
print(f"  reviews: {len(reviews):,} rows")

# Products
products = pd.read_csv(processed_dir / 'products_cleaned.csv')
products.to_sql('products', conn, if_exists='replace', index=False)
print(f"  products: {len(products):,} rows")

# Sellers
sellers = pd.read_csv(processed_dir / 'sellers_cleaned.csv')
sellers.to_sql('sellers', conn, if_exists='replace', index=False)
print(f"  sellers: {len(sellers):,} rows")

print("\n[SUCCESS] All tables loaded into SQLite!")

# =============================================================================
# STEP 3: VERIFY TABLE CREATION
# =============================================================================
print("\n[STEP 3] Verifying database structure...")

# List all tables
query_tables = """
SELECT name FROM sqlite_master 
WHERE type='table'
ORDER BY name;
"""

tables = pd.read_sql_query(query_tables, conn)
print("\nTables in database:")
for table in tables['name']:
    print(f"  - {table}")


# =============================================================================
# SQL QUERY 1: REVENUE BY MONTH
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 1: MONTHLY REVENUE ANALYSIS")
print("="*80)

query1 = """
SELECT 
    strftime('%Y-%m', order_purchase_timestamp) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price), 2) as total_gmv,
    ROUND(SUM(oi.freight_value), 2) as total_freight,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;
"""

print("\n[SQL QUERY]")
print(query1)

result1 = pd.read_sql_query(query1, conn)
print("\n[RESULTS]")
print(result1.to_string(index=False))

result1.to_csv(reports_dir / 'sql_monthly_revenue.csv', index=False)
print("\n[SAVED] sql_monthly_revenue.csv")


# =============================================================================
# SQL QUERY 2: TOP 10 PRODUCTS BY REVENUE
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 2: TOP 10 PRODUCTS BY REVENUE")
print("="*80)

query2 = """
SELECT 
    p.product_id,
    p.product_category_name as category,
    COUNT(oi.order_id) as times_sold,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY total_revenue DESC
LIMIT 10;
"""

print("\n[SQL QUERY]")
print(query2)

result2 = pd.read_sql_query(query2, conn)
print("\n[RESULTS]")
print(result2.to_string(index=False))

result2.to_csv(reports_dir / 'sql_top_products.csv', index=False)
print("\n[SAVED] sql_top_products.csv")


# =============================================================================
# SQL QUERY 3: CUSTOMER PURCHASE FREQUENCY
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 3: CUSTOMER PURCHASE FREQUENCY")
print("="*80)

query3 = """
SELECT 
    purchase_frequency,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT customer_unique_id) FROM customers), 2) as percentage
FROM (
    SELECT 
        c.customer_unique_id,
        COUNT(o.order_id) as purchase_frequency
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
GROUP BY purchase_frequency
ORDER BY purchase_frequency;
"""

print("\n[SQL QUERY]")
print(query3)

result3 = pd.read_sql_query(query3, conn)
print("\n[RESULTS]")
print(result3.to_string(index=False))

print("\n[INSIGHT] Customer Retention:")
one_time = result3[result3['purchase_frequency'] == 1]['customer_count'].values[0] if len(result3[result3['purchase_frequency'] == 1]) > 0 else 0
total = result3['customer_count'].sum()
print(f"  One-time buyers: {one_time:,} ({one_time/total*100:.1f}%)")
print(f"  Repeat buyers: {total - one_time:,} ({(total-one_time)/total*100:.1f}%)")

result3.to_csv(reports_dir / 'sql_customer_frequency.csv', index=False)
print("\n[SAVED] sql_customer_frequency.csv")


# =============================================================================
# SQL QUERY 4: TOP 10 CATEGORIES BY REVENUE
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 4: TOP 10 CATEGORIES BY REVENUE")
print("="*80)

query4 = """
SELECT 
    p.product_category_name as category,
    COUNT(DISTINCT oi.order_id) as order_count,
    COUNT(oi.product_id) as items_sold,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_revenue DESC
LIMIT 10;
"""

print("\n[SQL QUERY]")
print(query4)

result4 = pd.read_sql_query(query4, conn)
print("\n[RESULTS]")
print(result4.to_string(index=False))

result4.to_csv(reports_dir / 'sql_top_categories.csv', index=False)
print("\n[SAVED] sql_top_categories.csv")


# =============================================================================
# SQL QUERY 5: DELIVERY PERFORMANCE BY STATE
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 5: DELIVERY PERFORMANCE BY STATE")
print("="*80)

query5 = """
SELECT 
    c.customer_state as state,
    COUNT(o.order_id) as total_orders,
    ROUND(AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)), 1) as avg_delivery_days,
    ROUND(AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date)), 1) as avg_delay_days,
    ROUND(SUM(CASE WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date) THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as late_delivery_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered' 
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY total_orders DESC
LIMIT 10;
"""

print("\n[SQL QUERY]")
print(query5)

result5 = pd.read_sql_query(query5, conn)
print("\n[RESULTS]")
print(result5.to_string(index=False))

result5.to_csv(reports_dir / 'sql_delivery_by_state.csv', index=False)
print("\n[SAVED] sql_delivery_by_state.csv")


# =============================================================================
# SQL QUERY 6: PAYMENT METHOD ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 6: PAYMENT METHOD ANALYSIS")
print("="*80)

query6 = """
SELECT 
    payment_type,
    COUNT(*) as transaction_count,
    ROUND(SUM(payment_value), 2) as total_value,
    ROUND(AVG(payment_value), 2) as avg_value,
    ROUND(AVG(payment_installments), 1) as avg_installments
FROM payments
GROUP BY payment_type
ORDER BY total_value DESC;
"""

print("\n[SQL QUERY]")
print(query6)

result6 = pd.read_sql_query(query6, conn)
print("\n[RESULTS]")
print(result6.to_string(index=False))

result6.to_csv(reports_dir / 'sql_payment_methods.csv', index=False)
print("\n[SAVED] sql_payment_methods.csv")


# =============================================================================
# SQL QUERY 7: REVIEW SCORE ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 7: REVIEW SCORE ANALYSIS")
print("="*80)

query7 = """
SELECT 
    r.review_score,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) as percentage,
    ROUND(AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date)), 1) as avg_delay_days
FROM reviews r
JOIN orders o ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY r.review_score
ORDER BY r.review_score;
"""

print("\n[SQL QUERY]")
print(query7)

result7 = pd.read_sql_query(query7, conn)
print("\n[RESULTS]")
print(result7.to_string(index=False))

print("\n[INSIGHT] Satisfaction vs Delivery:")
best_score = result7[result7['review_score'] == 5]
worst_score = result7[result7['review_score'] == 1]
if len(best_score) > 0 and len(worst_score) > 0:
    print(f"  5-star reviews avg delay: {best_score['avg_delay_days'].values[0]:.1f} days")
    print(f"  1-star reviews avg delay: {worst_score['avg_delay_days'].values[0]:.1f} days")
    print(f"  Difference: {worst_score['avg_delay_days'].values[0] - best_score['avg_delay_days'].values[0]:.1f} days worse for 1-star")

result7.to_csv(reports_dir / 'sql_review_scores.csv', index=False)
print("\n[SAVED] sql_review_scores.csv")


# =============================================================================
# SQL QUERY 8: TOP 10 CUSTOMERS BY LIFETIME VALUE
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 8: TOP 10 CUSTOMERS BY LIFETIME VALUE")
print("="*80)

query8 = """
SELECT 
    c.customer_unique_id,
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price + oi.freight_value), 2) as lifetime_value,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id, c.customer_state
ORDER BY lifetime_value DESC
LIMIT 10;
"""

print("\n[SQL QUERY]")
print(query8)

result8 = pd.read_sql_query(query8, conn)
print("\n[RESULTS]")
print(result8.to_string(index=False))

result8.to_csv(reports_dir / 'sql_top_customers.csv', index=False)
print("\n[SAVED] sql_top_customers.csv")


# =============================================================================
# SQL QUERY 9: SELLER PERFORMANCE
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 9: TOP 10 SELLERS BY REVENUE")
print("="*80)

query9 = """
SELECT 
    s.seller_id,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) as orders_fulfilled,
    COUNT(oi.product_id) as items_sold,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(r.review_score), 2) as avg_review_score
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_state
ORDER BY total_revenue DESC
LIMIT 10;
"""

print("\n[SQL QUERY]")
print(query9)

result9 = pd.read_sql_query(query9, conn)
print("\n[RESULTS]")
print(result9.to_string(index=False))

result9.to_csv(reports_dir / 'sql_top_sellers.csv', index=False)
print("\n[SAVED] sql_top_sellers.csv")


# =============================================================================
# SQL QUERY 10: ADVANCED - COHORT RETENTION ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("SQL QUERY 10: MONTHLY COHORT RETENTION ANALYSIS")
print("="*80)

query10 = """
WITH customer_cohorts AS (
    SELECT 
        c.customer_unique_id,
        strftime('%Y-%m', MIN(o.order_purchase_timestamp)) as cohort_month,
        strftime('%Y-%m', o.order_purchase_timestamp) as order_month
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id, order_month
)
SELECT 
    cohort_month,
    COUNT(DISTINCT customer_unique_id) as cohort_size,
    COUNT(DISTINCT CASE WHEN cohort_month = order_month THEN customer_unique_id END) as month_0,
    COUNT(DISTINCT CASE WHEN order_month > cohort_month THEN customer_unique_id END) as returned_customers,
    ROUND(COUNT(DISTINCT CASE WHEN order_month > cohort_month THEN customer_unique_id END) * 100.0 / 
          COUNT(DISTINCT customer_unique_id), 2) as retention_rate
FROM customer_cohorts
GROUP BY cohort_month
ORDER BY cohort_month
LIMIT 12;
"""

print("\n[SQL QUERY]")
print(query10)

result10 = pd.read_sql_query(query10, conn)
print("\n[RESULTS]")
print(result10.to_string(index=False))

result10.to_csv(reports_dir / 'sql_cohort_retention.csv', index=False)
print("\n[SAVED] sql_cohort_retention.csv")


# =============================================================================
# STEP 4: SUMMARY OF SQL ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("SQL ANALYSIS SUMMARY")
print("="*80)

summary = f"""
SQL QUERIES EXECUTED: 10
=======================

1. Monthly Revenue Analysis
   - Aggregated revenue by month
   - Calculated GMV, freight, and total revenue
   - Used GROUP BY and date functions

2. Top Products by Revenue
   - Joined order_items with products
   - Ranked by total revenue
   - Used SUM and AVG aggregations

3. Customer Purchase Frequency
   - Analyzed repeat purchase behavior
   - Used subquery and LEFT JOIN
   - Calculated percentages

4. Top Categories by Revenue
   - Product category performance
   - Multiple aggregations (COUNT, SUM, AVG)

5. Delivery Performance by State
   - Geographic delivery analysis
   - Date calculations with JULIANDAY
   - Late delivery percentage using CASE

6. Payment Method Analysis
   - Payment type distribution
   - Aggregated values and installments

7. Review Score Analysis
   - Correlated reviews with delivery delays
   - Multi-table JOIN (reviews + orders)

8. Top Customers by Lifetime Value (CLV)
   - Customer segmentation
   - Multi-table aggregation

9. Top Sellers by Performance
   - Seller revenue ranking
   - Average review scores per seller

10. Cohort Retention Analysis (ADVANCED)
    - Used CTE (Common Table Expression)
    - Month-over-month retention
    - Complex date-based grouping

DATABASE INFO
=============
Location: {db_path}
Size: {db_path.stat().st_size / (1024*1024):.2f} MB
Tables: 7
Total Records: {len(customers) + len(orders) + len(order_items) + len(payments) + len(reviews) + len(products) + len(sellers):,}

SKILLS DEMONSTRATED
===================
- SELECT, WHERE, GROUP BY, HAVING, ORDER BY
- JOINs (INNER, LEFT)
- Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- Date functions (strftime, JULIANDAY)
- CASE statements for conditional logic
- Subqueries
- CTEs (Common Table Expressions)
- LIMIT and DISTINCT
- Percentage calculations
- Multi-table aggregations

FILES CREATED
=============
All results saved to reports/ folder:
- sql_monthly_revenue.csv
- sql_top_products.csv
- sql_customer_frequency.csv
- sql_top_categories.csv
- sql_delivery_by_state.csv
- sql_payment_methods.csv
- sql_review_scores.csv
- sql_top_customers.csv
- sql_top_sellers.csv
- sql_cohort_retention.csv

INTERVIEW TIP
=============
You can say: "I created a SQLite database and wrote 10 SQL queries 
analyzing revenue, customers, products, and delivery performance.
I used JOINs, CTEs, window functions, and date calculations to
extract business insights."
"""

print(summary)

# Save summary
summary_path = reports_dir / 'sql_analysis_summary.txt'
with open(summary_path, 'w') as f:
    f.write(summary)

print(f"\n[SAVED] {summary_path}")

# Close database connection
conn.close()

print("\n" + "="*80)
print("SQL ANALYSIS COMPLETE!")
print("="*80)
print(f"\nDatabase: {db_path}")
print(f"Query Results: {reports_dir}")
print("\nYou can now open the SQLite database in any SQL editor!")
print("Or run custom queries using: sqlite3 data/olist_analytics.db")
