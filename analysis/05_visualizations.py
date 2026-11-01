"""
OLIST ANALYTICS PRO - ADVANCED VISUALIZATIONS
Phase 5: Professional Charts and Dashboards

This script creates publication-quality visualizations for your portfolio.
Perfect for showing data visualization skills to recruiters.

Author: Your Name
Date: 2026-10-20
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sqlite3

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("OLIST E-COMMERCE ADVANCED VISUALIZATIONS")
print("="*80)

# =============================================================================
# STEP 1: SETUP
# =============================================================================
print("\n[STEP 1] Loading data...")

project_dir = Path(__file__).parent.parent
db_path = project_dir / 'data' / 'olist_analytics.db'
reports_dir = project_dir / 'reports'
charts_dir = reports_dir / 'charts'
charts_dir.mkdir(exist_ok=True)

# Connect to database
conn = sqlite3.connect(db_path)

print(f"Database: {db_path}")
print(f"Charts folder: {charts_dir}")


# =============================================================================
# CHART 1: REVENUE DASHBOARD
# =============================================================================
print("\n[CHART 1] Creating Revenue Dashboard...")

# Load monthly revenue data
monthly_revenue = pd.read_sql_query("""
    SELECT 
        strftime('%Y-%m', order_purchase_timestamp) as month,
        COUNT(DISTINCT o.order_id) as total_orders,
        ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
    ORDER BY month
""", conn)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Revenue Performance Dashboard', fontsize=20, fontweight='bold', y=0.995)

# 1. Monthly Revenue Trend
ax1 = axes[0, 0]
ax1.plot(monthly_revenue['month'], monthly_revenue['total_revenue'], 
         marker='o', linewidth=2.5, markersize=6, color='#2E86AB')
ax1.fill_between(range(len(monthly_revenue)), monthly_revenue['total_revenue'], 
                  alpha=0.3, color='#2E86AB')
ax1.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
ax1.set_xlabel('Month', fontsize=11)
ax1.set_ylabel('Revenue (R$)', fontsize=11)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1000:.0f}K'))

# 2. Monthly Order Count
ax2 = axes[0, 1]
ax2.bar(monthly_revenue['month'], monthly_revenue['total_orders'], 
        color='#A23B72', alpha=0.8, edgecolor='black')
ax2.set_title('Monthly Order Volume', fontsize=14, fontweight='bold')
ax2.set_xlabel('Month', fontsize=11)
ax2.set_ylabel('Number of Orders', fontsize=11)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3, axis='y')

# 3. Revenue Growth Rate
monthly_revenue['growth_rate'] = monthly_revenue['total_revenue'].pct_change() * 100
ax3 = axes[1, 0]
colors = ['green' if x >= 0 else 'red' for x in monthly_revenue['growth_rate']]
ax3.bar(monthly_revenue['month'], monthly_revenue['growth_rate'], 
        color=colors, alpha=0.7, edgecolor='black')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax3.set_title('Month-over-Month Growth Rate', fontsize=14, fontweight='bold')
ax3.set_xlabel('Month', fontsize=11)
ax3.set_ylabel('Growth Rate (%)', fontsize=11)
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3, axis='y')

# 4. Cumulative Revenue
monthly_revenue['cumulative_revenue'] = monthly_revenue['total_revenue'].cumsum()
ax4 = axes[1, 1]
ax4.plot(monthly_revenue['month'], monthly_revenue['cumulative_revenue'], 
         marker='s', linewidth=2.5, markersize=6, color='#F18F01')
ax4.fill_between(range(len(monthly_revenue)), monthly_revenue['cumulative_revenue'], 
                  alpha=0.3, color='#F18F01')
ax4.set_title('Cumulative Revenue', fontsize=14, fontweight='bold')
ax4.set_xlabel('Month', fontsize=11)
ax4.set_ylabel('Cumulative Revenue (R$)', fontsize=11)
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1000000:.1f}M'))

plt.tight_layout()
plt.savefig(charts_dir / '01_revenue_dashboard.png', dpi=300, bbox_inches='tight')
print(f"[SAVED] 01_revenue_dashboard.png")
plt.close()


# =============================================================================
# CHART 2: PRODUCT CATEGORY ANALYSIS
# =============================================================================
print("\n[CHART 2] Creating Product Category Analysis...")

top_categories = pd.read_sql_query("""
    SELECT 
        p.product_category_name as category,
        COUNT(DISTINCT oi.order_id) as order_count,
        ROUND(SUM(oi.price), 2) as total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_category_name
    ORDER BY total_revenue DESC
    LIMIT 15
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Product Category Performance', fontsize=18, fontweight='bold')

# 1. Top Categories by Revenue (Horizontal Bar)
ax1 = axes[0]
colors_revenue = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_categories)))
ax1.barh(top_categories['category'][::-1], top_categories['total_revenue'][::-1], 
         color=colors_revenue[::-1], edgecolor='black')
ax1.set_title('Top 15 Categories by Revenue', fontsize=14, fontweight='bold')
ax1.set_xlabel('Revenue (R$)', fontsize=11)
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1000:.0f}K'))
ax1.grid(True, alpha=0.3, axis='x')

# 2. Revenue vs Order Count (Scatter)
ax2 = axes[1]
scatter = ax2.scatter(top_categories['order_count'], top_categories['total_revenue'],
                     s=top_categories['total_revenue']/500, alpha=0.6, 
                     c=range(len(top_categories)), cmap='plasma', edgecolor='black')
ax2.set_title('Revenue vs Order Volume', fontsize=14, fontweight='bold')
ax2.set_xlabel('Number of Orders', fontsize=11)
ax2.set_ylabel('Revenue (R$)', fontsize=11)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1000:.0f}K'))
ax2.grid(True, alpha=0.3)

# Add category labels to top 5
for i, row in top_categories.head(5).iterrows():
    ax2.annotate(row['category'], 
                (row['order_count'], row['total_revenue']),
                fontsize=8, ha='right')

plt.tight_layout()
plt.savefig(charts_dir / '02_category_analysis.png', dpi=300, bbox_inches='tight')
print(f"[SAVED] 02_category_analysis.png")
plt.close()


# =============================================================================
# CHART 3: CUSTOMER BEHAVIOR ANALYSIS
# =============================================================================
print("\n[CHART 3] Creating Customer Behavior Analysis...")

# Purchase frequency
purchase_freq = pd.read_sql_query("""
    SELECT 
        purchase_frequency,
        COUNT(*) as customer_count
    FROM (
        SELECT 
            c.customer_unique_id,
            COUNT(o.order_id) as purchase_frequency
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_unique_id
    )
    GROUP BY purchase_frequency
    ORDER BY purchase_frequency
""", conn)

# Customer lifetime value distribution
clv_data = pd.read_sql_query("""
    SELECT 
        c.customer_unique_id,
        ROUND(SUM(oi.price + oi.freight_value), 2) as lifetime_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
""", conn)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Customer Behavior Analysis', fontsize=20, fontweight='bold', y=0.995)

# 1. Purchase Frequency Distribution
ax1 = axes[0, 0]
ax1.bar(purchase_freq['purchase_frequency'], purchase_freq['customer_count'],
        color='#E63946', alpha=0.8, edgecolor='black')
ax1.set_title('Customer Purchase Frequency', fontsize=14, fontweight='bold')
ax1.set_xlabel('Number of Purchases', fontsize=11)
ax1.set_ylabel('Number of Customers', fontsize=11)
ax1.set_yscale('log')
ax1.grid(True, alpha=0.3, axis='y')

# Add percentage labels
total_customers = purchase_freq['customer_count'].sum()
for i, row in purchase_freq.head(5).iterrows():
    pct = row['customer_count'] / total_customers * 100
    ax1.text(row['purchase_frequency'], row['customer_count'], 
            f'{pct:.1f}%', ha='center', va='bottom', fontsize=9)

# 2. Customer Lifetime Value Distribution
ax2 = axes[0, 1]
ax2.hist(clv_data['lifetime_value'], bins=50, color='#457B9D', 
         alpha=0.7, edgecolor='black')
ax2.set_title('Customer Lifetime Value Distribution', fontsize=14, fontweight='bold')
ax2.set_xlabel('Lifetime Value (R$)', fontsize=11)
ax2.set_ylabel('Number of Customers', fontsize=11)
ax2.axvline(clv_data['lifetime_value'].median(), color='red', 
           linestyle='--', linewidth=2, label=f'Median: R$ {clv_data["lifetime_value"].median():.2f}')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# 3. Customer Segmentation (Pie Chart)
ax3 = axes[1, 0]
segments = {
    'One-time': purchase_freq[purchase_freq['purchase_frequency'] == 1]['customer_count'].sum(),
    'Two-time': purchase_freq[purchase_freq['purchase_frequency'] == 2]['customer_count'].sum(),
    '3+ times': purchase_freq[purchase_freq['purchase_frequency'] >= 3]['customer_count'].sum()
}
colors_seg = ['#F4A261', '#E76F51', '#264653']
wedges, texts, autotexts = ax3.pie(segments.values(), labels=segments.keys(), autopct='%1.1f%%',
                                     colors=colors_seg, startangle=90, explode=(0.05, 0, 0))
ax3.set_title('Customer Retention Segments', fontsize=14, fontweight='bold')
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

# 4. Top States by Customer Count
top_states = pd.read_sql_query("""
    SELECT customer_state, COUNT(*) as customer_count
    FROM customers
    GROUP BY customer_state
    ORDER BY customer_count DESC
    LIMIT 10
""", conn)

ax4 = axes[1, 1]
ax4.barh(top_states['customer_state'][::-1], top_states['customer_count'][::-1],
         color='#2A9D8F', alpha=0.8, edgecolor='black')
ax4.set_title('Top 10 States by Customer Count', fontsize=14, fontweight='bold')
ax4.set_xlabel('Number of Customers', fontsize=11)
ax4.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig(charts_dir / '03_customer_behavior.png', dpi=300, bbox_inches='tight')
print(f"[SAVED] 03_customer_behavior.png")
plt.close()


# =============================================================================
# CHART 4: DELIVERY PERFORMANCE ANALYSIS
# =============================================================================
print("\n[CHART 4] Creating Delivery Performance Analysis...")

delivery_data = pd.read_sql_query("""
    SELECT 
        JULIANDAY(order_delivered_customer_date) - JULIANDAY(order_estimated_delivery_date) as delay_days,
        review_score
    FROM orders o
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
""", conn)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Delivery Performance Analysis', fontsize=20, fontweight='bold', y=0.995)

# 1. Delivery Delay Distribution
ax1 = axes[0, 0]
ax1.hist(delivery_data['delay_days'], bins=60, color='#E76F51', 
         alpha=0.7, edgecolor='black')
ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='On-time threshold')
ax1.set_title('Delivery Delay Distribution', fontsize=14, fontweight='bold')
ax1.set_xlabel('Delay (days, negative = early)', fontsize=11)
ax1.set_ylabel('Number of Orders', fontsize=11)
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 2. On-time vs Late Deliveries (Pie)
ax2 = axes[0, 1]
on_time = (delivery_data['delay_days'] <= 0).sum()
late = (delivery_data['delay_days'] > 0).sum()
labels = [f'On-time/Early\n({on_time:,})', f'Late\n({late:,})']
colors_delivery = ['#2A9D8F', '#E76F51']
wedges, texts, autotexts = ax2.pie([on_time, late], labels=labels, autopct='%1.1f%%',
                                     colors=colors_delivery, startangle=90)
ax2.set_title('Delivery Performance', fontsize=14, fontweight='bold')
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(12)
    autotext.set_fontweight('bold')

# 3. Review Score by Delivery Performance
ax3 = axes[1, 0]
delivery_categories = pd.cut(delivery_data['delay_days'], 
                              bins=[-200, -10, 0, 10, 200],
                              labels=['Very Early', 'On-time', 'Slightly Late', 'Very Late'])
delivery_data['category'] = delivery_categories

avg_scores = delivery_data.groupby('category')['review_score'].mean()
colors_bars = ['#2A9D8F', '#F4A261', '#E76F51', '#BC4749']
ax3.bar(range(len(avg_scores)), avg_scores.values, color=colors_bars, 
        alpha=0.8, edgecolor='black')
ax3.set_xticks(range(len(avg_scores)))
ax3.set_xticklabels(avg_scores.index, rotation=15)
ax3.set_title('Average Review Score by Delivery Performance', fontsize=14, fontweight='bold')
ax3.set_ylabel('Average Review Score', fontsize=11)
ax3.set_ylim([0, 5])
ax3.axhline(y=delivery_data['review_score'].mean(), color='red', 
           linestyle='--', linewidth=2, label='Overall Average')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, v in enumerate(avg_scores.values):
    ax3.text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold')

# 4. Delay vs Review Score (Scatter)
ax4 = axes[1, 1]
# Sample data for better visualization
sample = delivery_data.sample(min(5000, len(delivery_data)))
scatter = ax4.scatter(sample['delay_days'], sample['review_score'],
                     alpha=0.3, s=10, c=sample['review_score'], cmap='RdYlGn')
ax4.set_title('Delivery Delay vs Review Score', fontsize=14, fontweight='bold')
ax4.set_xlabel('Delay (days)', fontsize=11)
ax4.set_ylabel('Review Score', fontsize=11)
ax4.axvline(x=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
ax4.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax4, label='Review Score')

plt.tight_layout()
plt.savefig(charts_dir / '04_delivery_performance.png', dpi=300, bbox_inches='tight')
print(f"[SAVED] 04_delivery_performance.png")
plt.close()


# =============================================================================
# CHART 5: PAYMENT ANALYSIS
# =============================================================================
print("\n[CHART 5] Creating Payment Analysis...")

payment_data = pd.read_sql_query("""
    SELECT 
        payment_type,
        COUNT(*) as transaction_count,
        SUM(payment_value) as total_value,
        AVG(payment_installments) as avg_installments
    FROM payments
    GROUP BY payment_type
    ORDER BY total_value DESC
""", conn)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Payment Method Analysis', fontsize=18, fontweight='bold')

# 1. Payment Methods Distribution (Pie)
ax1 = axes[0]
colors_payment = plt.cm.Set3(range(len(payment_data)))
wedges, texts, autotexts = ax1.pie(payment_data['transaction_count'], 
                                     labels=payment_data['payment_type'],
                                     autopct='%1.1f%%', colors=colors_payment, startangle=90)
ax1.set_title('Payment Method Distribution', fontsize=14, fontweight='bold')
for autotext in autotexts:
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

# 2. Revenue by Payment Method
ax2 = axes[1]
ax2.bar(payment_data['payment_type'], payment_data['total_value']/1000000,
        color=colors_payment, alpha=0.8, edgecolor='black')
ax2.set_title('Revenue by Payment Method', fontsize=14, fontweight='bold')
ax2.set_xlabel('Payment Method', fontsize=11)
ax2.set_ylabel('Revenue (R$ millions)', fontsize=11)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, v in enumerate(payment_data['total_value']/1000000):
    ax2.text(i, v + 0.2, f'R$ {v:.1f}M', ha='center', fontweight='bold')

# 3. Average Installments by Payment Type
ax3 = axes[2]
ax3.barh(payment_data['payment_type'], payment_data['avg_installments'],
         color=colors_payment, alpha=0.8, edgecolor='black')
ax3.set_title('Average Installments by Payment Type', fontsize=14, fontweight='bold')
ax3.set_xlabel('Average Installments', fontsize=11)
ax3.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, v in enumerate(payment_data['avg_installments']):
    ax3.text(v + 0.1, i, f'{v:.1f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig(charts_dir / '05_payment_analysis.png', dpi=300, bbox_inches='tight')
print(f"[SAVED] 05_payment_analysis.png")
plt.close()


# =============================================================================
# CHART 6: EXECUTIVE SUMMARY DASHBOARD
# =============================================================================
print("\n[CHART 6] Creating Executive Summary Dashboard...")

# Get key metrics
metrics = pd.read_sql_query("""
    SELECT 
        COUNT(DISTINCT o.order_id) as total_orders,
        COUNT(DISTINCT c.customer_unique_id) as total_customers,
        ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
        ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
        ROUND(AVG(r.review_score), 2) as avg_review_score
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
""", conn)

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

fig.suptitle('Executive Summary Dashboard', fontsize=22, fontweight='bold', y=0.98)

# KPI Boxes
kpi_data = [
    ('Total Revenue', f"R$ {metrics['total_revenue'].values[0]/1000000:.2f}M", '#2E86AB'),
    ('Total Orders', f"{metrics['total_orders'].values[0]:,}", '#A23B72'),
    ('Total Customers', f"{metrics['total_customers'].values[0]:,}", '#F18F01'),
    ('Avg Order Value', f"R$ {metrics['avg_order_value'].values[0]:.2f}", '#2A9D8F'),
    ('Avg Review Score', f"{metrics['avg_review_score'].values[0]:.2f} / 5.0", '#E76F51')
]

for i, (title, value, color) in enumerate(kpi_data[:3]):
    ax = fig.add_subplot(gs[0, i])
    ax.text(0.5, 0.6, value, ha='center', va='center', 
           fontsize=28, fontweight='bold', color=color)
    ax.text(0.5, 0.3, title, ha='center', va='center', 
           fontsize=14, color='gray')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, 
                               fill=False, edgecolor=color, linewidth=3))

# Revenue trend (small)
ax1 = fig.add_subplot(gs[1, :2])
ax1.plot(monthly_revenue['month'], monthly_revenue['total_revenue'], 
        marker='o', linewidth=2, markersize=4, color='#2E86AB')
ax1.fill_between(range(len(monthly_revenue)), monthly_revenue['total_revenue'], 
                 alpha=0.3, color='#2E86AB')
ax1.set_title('Revenue Trend', fontsize=12, fontweight='bold')
ax1.tick_params(axis='x', rotation=45, labelsize=8)
ax1.grid(True, alpha=0.3)

# Top categories (small)
ax2 = fig.add_subplot(gs[1, 2])
top5_cat = top_categories.head(5)
ax2.barh(range(len(top5_cat)), top5_cat['total_revenue'], color='#A23B72', alpha=0.8)
ax2.set_yticks(range(len(top5_cat)))
ax2.set_yticklabels(top5_cat['category'], fontsize=9)
ax2.set_title('Top 5 Categories', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# Customer segments
ax3 = fig.add_subplot(gs[2, 0])
segments_small = [segments['One-time'], segments['Two-time'], segments['3+ times']]
ax3.pie(segments_small, labels=['One-time', 'Two-time', '3+ times'], 
       autopct='%1.1f%%', colors=['#F4A261', '#E76F51', '#264653'])
ax3.set_title('Customer Segments', fontsize=12, fontweight='bold')

# Delivery performance
ax4 = fig.add_subplot(gs[2, 1])
ax4.bar(['On-time/Early', 'Late'], [on_time, late], 
       color=['#2A9D8F', '#E76F51'], alpha=0.8, edgecolor='black')
ax4.set_title('Delivery Performance', fontsize=12, fontweight='bold')
ax4.set_ylabel('Orders', fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')

# Payment methods
ax5 = fig.add_subplot(gs[2, 2])
top3_payment = payment_data.head(3)
ax5.bar(top3_payment['payment_type'], top3_payment['total_value']/1000000,
       color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8, edgecolor='black')
ax5.set_title('Top Payment Methods', fontsize=12, fontweight='bold')
ax5.set_ylabel('Revenue (R$ M)', fontsize=10)
ax5.tick_params(axis='x', rotation=45, labelsize=9)
ax5.grid(True, alpha=0.3, axis='y')

plt.savefig(charts_dir / '06_executive_dashboard.png', dpi=300, bbox_inches='tight')
print(f"[SAVED] 06_executive_dashboard.png")
plt.close()

# Close database connection
conn.close()

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "="*80)
print("VISUALIZATION COMPLETE!")
print("="*80)

summary = """
PROFESSIONAL CHARTS CREATED: 6
===============================

1. Revenue Dashboard (4 panels)
   - Monthly revenue trend with growth rates
   - Order volume over time
   - Cumulative revenue
   
2. Product Category Analysis (2 panels)
   - Top 15 categories by revenue
   - Revenue vs order volume scatter

3. Customer Behavior Analysis (4 panels)
   - Purchase frequency distribution
   - Customer lifetime value histogram
   - Customer segmentation pie chart
   - Geographic distribution

4. Delivery Performance Analysis (4 panels)
   - Delivery delay distribution
   - On-time vs late percentage
   - Review scores by delivery performance
   - Delay vs satisfaction scatter plot

5. Payment Analysis (3 panels)
   - Payment method distribution
   - Revenue by payment method
   - Average installments

6. Executive Summary Dashboard (8 panels)
   - Key metrics (KPIs)
   - Mini versions of all major insights
   - Perfect for presentations!

ALL FILES SAVED TO: {}

INTERVIEW TIP
=============
Tell recruiters: "I created 6 professional dashboards with 20+ 
visualizations using Python (Matplotlib and Seaborn) showing
revenue trends, customer segmentation, delivery performance,
and payment analysis. These charts tell the complete business story."
""".format(charts_dir)

print(summary)

# Save summary
summary_path = reports_dir / 'visualization_summary.txt'
with open(summary_path, 'w') as f:
    f.write(summary)

print(f"\n[SAVED] {summary_path}")
print("\nYou now have 6 professional charts ready for your portfolio!")
print("Use chart #6 (Executive Dashboard) for presentations and interviews!")
