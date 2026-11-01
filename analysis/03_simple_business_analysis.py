"""
OLIST ANALYTICS PRO - SIMPLE BUSINESS ANALYSIS
Phase 3: Revenue, Customer, and Product Analysis

This script answers key business questions using clean data.
Perfect for explaining to recruiters what insights you found.

Author: Your Name
Date: 2026-10-20
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configure plotting
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

print("="*80)
print("OLIST E-COMMERCE BUSINESS ANALYSIS")
print("="*80)

# =============================================================================
# STEP 1: LOAD CLEANED DATA
# =============================================================================
print("\n[STEP 1] Loading cleaned datasets...")

project_dir = Path(__file__).parent.parent
processed_dir = project_dir / 'data' / 'processed'
reports_dir = project_dir / 'reports'
reports_dir.mkdir(exist_ok=True)

# Load cleaned data
master_orders = pd.read_csv(processed_dir / 'master_orders.csv')
order_items = pd.read_csv(processed_dir / 'order_items_cleaned.csv')
products = pd.read_csv(processed_dir / 'products_cleaned.csv')
customers = pd.read_csv(processed_dir / 'customers_cleaned.csv')

# Convert dates
master_orders['order_purchase_timestamp'] = pd.to_datetime(master_orders['order_purchase_timestamp'])
order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'])

print(f"Loaded {len(master_orders):,} orders")
print(f"Loaded {len(order_items):,} order items")
print(f"Loaded {len(products):,} products")
print(f"Loaded {len(customers):,} customers")


# =============================================================================
# STEP 2: REVENUE ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("[STEP 2] REVENUE ANALYSIS")
print("="*80)

# Overall revenue metrics
total_gmv = master_orders['items_price_total'].sum()
total_freight = master_orders['items_freight_total'].sum()
total_revenue = master_orders['items_total_value'].sum()

print(f"\n[METRICS] Overall Revenue:")
print(f"  Total GMV (Gross Merchandise Value): R$ {total_gmv:,.2f}")
print(f"  Total Freight Revenue: R$ {total_freight:,.2f}")
print(f"  Total Revenue: R$ {total_revenue:,.2f}")
print(f"  Freight as % of GMV: {(total_freight/total_gmv)*100:.1f}%")

# Average order metrics
delivered_orders = master_orders[master_orders['order_status'] == 'delivered']
avg_order_value = delivered_orders['items_total_value'].mean()
median_order_value = delivered_orders['items_total_value'].median()

print(f"\n[METRICS] Order Value:")
print(f"  Average Order Value (AOV): R$ {avg_order_value:.2f}")
print(f"  Median Order Value: R$ {median_order_value:.2f}")
print(f"  Min Order Value: R$ {delivered_orders['items_total_value'].min():.2f}")
print(f"  Max Order Value: R$ {delivered_orders['items_total_value'].max():.2f}")

# Monthly revenue trend
master_orders['year_month'] = master_orders['order_purchase_timestamp'].dt.to_period('M')
monthly_revenue = master_orders.groupby('year_month')['items_total_value'].sum()

print(f"\n[ANALYSIS] Monthly Revenue Trend:")
print(f"  Best month: {monthly_revenue.idxmax()} (R$ {monthly_revenue.max():,.2f})")
print(f"  Worst month: {monthly_revenue.idxmin()} (R$ {monthly_revenue.min():,.2f})")

# Plot monthly revenue
plt.figure(figsize=(14, 6))
monthly_revenue_values = monthly_revenue.values
monthly_revenue_index = [str(x) for x in monthly_revenue.index]
plt.plot(monthly_revenue_index, monthly_revenue_values, marker='o', linewidth=2, markersize=6)
plt.title('Monthly Revenue Trend', fontsize=16, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Revenue (R$)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(reports_dir / 'monthly_revenue_trend.png', dpi=300, bbox_inches='tight')
print(f"\n[CHART] Saved: monthly_revenue_trend.png")
plt.close()


# =============================================================================
# STEP 3: PRODUCT ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("[STEP 3] PRODUCT ANALYSIS")
print("="*80)

# Merge order items with products
items_with_products = order_items.merge(products, on='product_id', how='left')

# Revenue by category
category_revenue = items_with_products.groupby('product_category_name').agg({
    'price': 'sum',
    'order_id': 'count'
}).reset_index()
category_revenue.columns = ['category', 'total_revenue', 'items_sold']
category_revenue = category_revenue.sort_values('total_revenue', ascending=False)

print(f"\n[ANALYSIS] Top 10 Categories by Revenue:")
top_10_categories = category_revenue.head(10)
for idx, row in top_10_categories.iterrows():
    print(f"  {row['category']:30s} R$ {row['total_revenue']:>12,.2f}  ({row['items_sold']:,} items)")

# Plot top categories
plt.figure(figsize=(12, 8))
plt.barh(top_10_categories['category'][::-1], top_10_categories['total_revenue'][::-1], color='steelblue')
plt.title('Top 10 Product Categories by Revenue', fontsize=16, fontweight='bold')
plt.xlabel('Revenue (R$)', fontsize=12)
plt.ylabel('Category', fontsize=12)
plt.tight_layout()
plt.savefig(reports_dir / 'top_categories_revenue.png', dpi=300, bbox_inches='tight')
print(f"\n[CHART] Saved: top_categories_revenue.png")
plt.close()

# Best selling products
product_sales = items_with_products.groupby('product_id').agg({
    'price': ['sum', 'mean', 'count']
}).reset_index()
product_sales.columns = ['product_id', 'total_revenue', 'avg_price', 'quantity_sold']
product_sales = product_sales.sort_values('quantity_sold', ascending=False)

print(f"\n[ANALYSIS] Top 10 Best-Selling Products:")
print(f"  Total unique products sold: {product_sales.shape[0]:,}")
print(f"\n  Top sellers:")
for idx, row in product_sales.head(10).iterrows():
    print(f"    Product {row['product_id'][:8]}... : {row['quantity_sold']:,} units, R$ {row['total_revenue']:,.2f}")


# =============================================================================
# STEP 4: CUSTOMER ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("[STEP 4] CUSTOMER ANALYSIS")
print("="*80)

# Customer repeat purchase analysis
customer_orders = customers.merge(
    master_orders[['customer_id', 'order_id', 'items_total_value']],
    on='customer_id',
    how='inner'
)

# Count orders per unique customer
orders_per_customer = customer_orders.groupby('customer_unique_id').size()

print(f"\n[ANALYSIS] Customer Purchase Behavior:")
print(f"  Total unique customers: {customers['customer_unique_id'].nunique():,}")
print(f"  Total orders: {len(master_orders):,}")
print(f"  Average orders per customer: {orders_per_customer.mean():.2f}")

# Distribution of orders per customer
print(f"\n  Customer Segments:")
one_time = (orders_per_customer == 1).sum()
two_time = (orders_per_customer == 2).sum()
three_plus = (orders_per_customer >= 3).sum()

total_unique_customers = customers['customer_unique_id'].nunique()
print(f"    One-time buyers: {one_time:,} ({one_time/total_unique_customers*100:.1f}%)")
print(f"    Two-time buyers: {two_time:,} ({two_time/total_unique_customers*100:.1f}%)")
print(f"    3+ time buyers: {three_plus:,} ({three_plus/total_unique_customers*100:.1f}%)")

# Customer lifetime value (CLV)
customer_ltv = customer_orders.groupby('customer_unique_id')['items_total_value'].sum()

print(f"\n[METRICS] Customer Lifetime Value:")
print(f"  Mean CLV: R$ {customer_ltv.mean():.2f}")
print(f"  Median CLV: R$ {customer_ltv.median():.2f}")
print(f"  Max CLV: R$ {customer_ltv.max():.2f}")

# Top customers
print(f"\n  Top 5 customers by total spend:")
top_customers = customer_ltv.nlargest(5)
for idx, (customer_id, value) in enumerate(top_customers.items(), 1):
    print(f"    {idx}. Customer {customer_id[:8]}... : R$ {value:,.2f}")

# Geographic distribution
state_revenue = customer_orders.groupby('customer_state').agg({
    'items_total_value': 'sum',
    'customer_unique_id': 'nunique'
}).reset_index()
state_revenue.columns = ['state', 'total_revenue', 'unique_customers']
state_revenue = state_revenue.sort_values('total_revenue', ascending=False)

print(f"\n[ANALYSIS] Top 10 States by Revenue:")
for idx, row in state_revenue.head(10).iterrows():
    print(f"  {row['state']:2s}  R$ {row['total_revenue']:>12,.2f}  ({row['unique_customers']:,} customers)")


# =============================================================================
# STEP 5: DELIVERY PERFORMANCE ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("[STEP 5] DELIVERY PERFORMANCE ANALYSIS")
print("="*80)

# Analyze only delivered orders
delivered = master_orders[master_orders['order_status'] == 'delivered'].copy()

# Remove rows with missing delivery delay
delivered_with_delay = delivered[delivered['delivery_delay_days'].notna()]

print(f"\n[METRICS] Delivery Performance:")
print(f"  Delivered orders analyzed: {len(delivered_with_delay):,}")
print(f"  Mean delivery time: {delivered_with_delay['actual_delivery_days'].mean():.1f} days")
print(f"  Mean estimated time: {delivered_with_delay['estimated_delivery_days'].mean():.1f} days")
print(f"  Mean delay: {delivered_with_delay['delivery_delay_days'].mean():.1f} days")

# Late delivery analysis
on_time = delivered_with_delay[delivered_with_delay['delivery_delay_days'] <= 0]
late = delivered_with_delay[delivered_with_delay['delivery_delay_days'] > 0]

print(f"\n[ANALYSIS] On-Time Performance:")
print(f"  On-time/early: {len(on_time):,} ({len(on_time)/len(delivered_with_delay)*100:.1f}%)")
print(f"  Late: {len(late):,} ({len(late)/len(delivered_with_delay)*100:.1f}%)")

if len(late) > 0:
    print(f"\n  Late Delivery Statistics:")
    print(f"    Mean delay: {late['delivery_delay_days'].mean():.1f} days")
    print(f"    Median delay: {late['delivery_delay_days'].median():.1f} days")
    print(f"    Max delay: {late['delivery_delay_days'].max():.0f} days")

# Plot delivery delay distribution
plt.figure(figsize=(12, 6))
plt.hist(delivered_with_delay['delivery_delay_days'], bins=50, color='coral', edgecolor='black', alpha=0.7)
plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='On-time threshold')
plt.title('Distribution of Delivery Delays', fontsize=16, fontweight='bold')
plt.xlabel('Delay (days, negative = early)', fontsize=12)
plt.ylabel('Number of Orders', fontsize=12)
plt.legend()
plt.tight_layout()
plt.savefig(reports_dir / 'delivery_delay_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n[CHART] Saved: delivery_delay_distribution.png")
plt.close()


# =============================================================================
# STEP 6: REVIEW SCORE ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("[STEP 6] CUSTOMER SATISFACTION ANALYSIS")
print("="*80)

# Review scores for delivered orders
delivered_with_review = delivered[delivered['review_score'].notna()]

print(f"\n[METRICS] Customer Satisfaction:")
print(f"  Orders with reviews: {len(delivered_with_review):,}")
print(f"  Average review score: {delivered_with_review['review_score'].mean():.2f}")
print(f"  Median review score: {delivered_with_review['review_score'].median():.0f}")

# Review distribution
review_dist = delivered_with_review['review_score'].value_counts().sort_index()
print(f"\n[ANALYSIS] Review Score Distribution:")
for score, count in review_dist.items():
    pct = (count / len(delivered_with_review)) * 100
    print(f"  Score {score}: {count:,} ({pct:.1f}%)")

# Satisfaction vs delivery performance
print(f"\n[ANALYSIS] Satisfaction vs Delivery Performance:")

# Compare on-time vs late delivery reviews
on_time_reviews = delivered_with_review[delivered_with_review['delivery_delay_days'] <= 0]['review_score'].mean()
late_reviews = delivered_with_review[delivered_with_review['delivery_delay_days'] > 0]['review_score'].mean()

print(f"  Average score for on-time deliveries: {on_time_reviews:.2f}")
print(f"  Average score for late deliveries: {late_reviews:.2f}")
print(f"  Difference: {on_time_reviews - late_reviews:.2f} points")

# Plot review scores
plt.figure(figsize=(10, 6))
review_counts = delivered_with_review['review_score'].value_counts().sort_index()
plt.bar(review_counts.index, review_counts.values, color='gold', edgecolor='black')
plt.title('Customer Review Score Distribution', fontsize=16, fontweight='bold')
plt.xlabel('Review Score', fontsize=12)
plt.ylabel('Number of Reviews', fontsize=12)
plt.xticks([1, 2, 3, 4, 5])
plt.tight_layout()
plt.savefig(reports_dir / 'review_score_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n[CHART] Saved: review_score_distribution.png")
plt.close()


# =============================================================================
# STEP 7: KEY BUSINESS INSIGHTS
# =============================================================================
print("\n" + "="*80)
print("[STEP 7] KEY BUSINESS INSIGHTS")
print("="*80)

insights = f"""
EXECUTIVE SUMMARY
=================

1. REVENUE PERFORMANCE
   - Total Revenue: R$ {total_revenue:,.2f}
   - Average Order Value: R$ {avg_order_value:.2f}
   - Freight represents {(total_freight/total_gmv)*100:.1f}% of GMV

2. CUSTOMER BEHAVIOR
   - {total_unique_customers:,} unique customers made {len(master_orders):,} orders
   - Only {three_plus/total_unique_customers*100:.1f}% are repeat buyers (3+ orders)
   - Average Customer Lifetime Value: R$ {customer_ltv.mean():.2f}

3. PRODUCT INSIGHTS
   - Top category: {top_10_categories.iloc[0]['category']} (R$ {top_10_categories.iloc[0]['total_revenue']:,.2f})
   - {product_sales.shape[0]:,} unique products sold
   - High product variety with low repeat purchase rate

4. DELIVERY PERFORMANCE
   - {len(late)/len(delivered_with_delay)*100:.1f}% of orders delivered late
   - Average delay: {delivered_with_delay['delivery_delay_days'].mean():.1f} days (overall negative = generally early)
   - On-time delivery critical for satisfaction

5. CUSTOMER SATISFACTION
   - Average review: {delivered_with_review['review_score'].mean():.2f}/5.0
   - {(review_dist[5] / len(delivered_with_review)) * 100:.1f}% gave 5-star reviews
   - Late deliveries score {on_time_reviews - late_reviews:.2f} points lower

RECOMMENDATIONS
===============

1. IMPROVE RETENTION
   - Only {three_plus:,} customers (3+ orders) drive repeat business
   - Implement loyalty program or email campaigns
   - Target one-time buyers with personalized offers

2. OPTIMIZE DELIVERY
   - Late deliveries correlate with lower satisfaction
   - Focus on {len(late):,} late orders ({len(late)/len(delivered_with_delay)*100:.1f}%)
   - Investigate bottlenecks causing delays

3. LEVERAGE TOP CATEGORIES
   - Top 3 categories drive significant revenue
   - Expand inventory in high-performing categories
   - Cross-sell complementary products

4. ADDRESS LOW SATISFACTION
   - {(review_dist[1] + review_dist[2]) / len(delivered_with_review) * 100:.1f}% gave 1-2 star reviews
   - Follow up with unhappy customers
   - Identify root causes (delivery, quality, service)

5. REDUCE FREIGHT COSTS
   - Freight is {(total_freight/total_gmv)*100:.1f}% of GMV
   - Negotiate better shipping rates
   - Offer free shipping threshold to increase AOV
"""

print(insights)

# Save insights
insights_path = reports_dir / 'business_insights.txt'
with open(insights_path, 'w', encoding='utf-8') as f:
    f.write(insights)

print(f"\n[SUCCESS] Insights saved to: {insights_path}")


# =============================================================================
# STEP 8: SAVE SUMMARY METRICS
# =============================================================================
print("\n" + "="*80)
print("[STEP 8] SAVING SUMMARY METRICS")
print("="*80)

# Create summary dataframe
summary_metrics = pd.DataFrame({
    'Metric': [
        'Total Revenue',
        'Total Orders',
        'Total Customers',
        'Average Order Value',
        'Customer Lifetime Value (mean)',
        'Repeat Customer Rate',
        'Late Delivery Rate',
        'Average Review Score',
        '5-Star Review Rate'
    ],
    'Value': [
        f"R$ {total_revenue:,.2f}",
        f"{len(master_orders):,}",
        f"{total_unique_customers:,}",
        f"R$ {avg_order_value:.2f}",
        f"R$ {customer_ltv.mean():.2f}",
        f"{three_plus/total_unique_customers*100:.1f}%",
        f"{len(late)/len(delivered_with_delay)*100:.1f}%",
        f"{delivered_with_review['review_score'].mean():.2f}",
        f"{(review_dist[5] / len(delivered_with_review)) * 100:.1f}%"
    ]
})

summary_metrics.to_csv(reports_dir / 'summary_metrics.csv', index=False)
print(f"\n[SUCCESS] Summary metrics saved to: summary_metrics.csv")

print("\n" + "="*80)
print("BUSINESS ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated Files:")
print("  - monthly_revenue_trend.png")
print("  - top_categories_revenue.png")
print("  - delivery_delay_distribution.png")
print("  - review_score_distribution.png")
print("  - business_insights.txt")
print("  - summary_metrics.csv")
print("\nNext Steps:")
print("  1. Review charts and insights")
print("  2. Create SQL analysis queries")
print("  3. Build Power BI dashboard")
print("  4. Prepare presentation for recruiters")
