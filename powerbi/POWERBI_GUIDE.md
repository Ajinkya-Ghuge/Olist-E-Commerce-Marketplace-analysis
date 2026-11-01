# Power BI Dashboard Guide

## Step-by-Step Setup

### 1. Load Data into Power BI

**Option A: Load Master Table (Easiest!)**
1. Open Power BI Desktop
2. Click **Home** → **Get Data** → **Text/CSV**
3. Navigate to: `data/processed/master_orders.csv`
4. Click **Load**

**Option B: Load Multiple Tables (More Advanced)**
If you want separate tables:
- `data/processed/orders_cleaned.csv`
- `data/processed/order_items_cleaned.csv`
- `data/processed/customers_cleaned.csv`
- `data/processed/products_cleaned.csv`
- `data/processed/payments_cleaned.csv`
- `data/processed/reviews_cleaned.csv`

Then create relationships in Power BI Model view using `order_id` as the key.

---

### 2. Transform Data (Power Query)

After loading, click **Transform Data**:

#### Fix Date Columns:
1. Select date columns: `order_purchase_timestamp`, `order_delivered_customer_date`, `order_estimated_delivery_date`
2. Right-click → **Change Type** → **Date/Time**

#### Remove Nulls (Optional):
1. Click column header → **Remove Rows** → **Remove Blank Rows**

#### Create Calculated Columns (if needed):
```
Year = YEAR(master_orders[order_purchase_timestamp])
Month = FORMAT(master_orders[order_purchase_timestamp], "YYYY-MM")
Quarter = QUARTER(master_orders[order_purchase_timestamp])
```

Click **Close & Apply**

---

### 3. Create DAX Measures

In Power BI, click **Modeling** → **New Measure** and add these:

#### Revenue Measures
```dax
Total Revenue = SUM(master_orders[items_total_value])
```

```dax
Total GMV = SUM(master_orders[items_price_total])
```

```dax
Total Freight = SUM(master_orders[items_freight_total])
```

```dax
Average Order Value = 
DIVIDE(
    [Total Revenue],
    [Total Orders],
    0
)
```

#### Order Measures
```dax
Total Orders = DISTINCTCOUNT(master_orders[order_id])
```

```dax
Delivered Orders = 
CALCULATE(
    [Total Orders],
    master_orders[order_status] = "delivered"
)
```

#### Customer Measures
```dax
Total Customers = DISTINCTCOUNT(master_orders[customer_id])
```

```dax
Unique Customers = DISTINCTCOUNT(master_orders[customer_unique_id])
```

```dax
Repeat Customers = 
VAR CustomerOrders = 
    SUMMARIZE(
        master_orders,
        master_orders[customer_unique_id],
        "OrderCount", DISTINCTCOUNT(master_orders[order_id])
    )
RETURN
    COUNTROWS(
        FILTER(
            CustomerOrders,
            [OrderCount] > 1
        )
    )
```

```dax
Repeat Customer Rate = 
DIVIDE(
    [Repeat Customers],
    [Unique Customers],
    0
)
```

#### Delivery Measures
```dax
Average Delivery Days = AVERAGE(master_orders[actual_delivery_days])
```

```dax
Late Deliveries = 
CALCULATE(
    [Total Orders],
    master_orders[delivery_delay_days] > 0
)
```

```dax
Late Delivery Rate = 
DIVIDE(
    [Late Deliveries],
    [Delivered Orders],
    0
)
```

```dax
On-Time Deliveries = 
CALCULATE(
    [Total Orders],
    master_orders[delivery_delay_days] <= 0
)
```

#### Review Measures
```dax
Average Review Score = AVERAGE(master_orders[review_score])
```

```dax
5-Star Reviews = 
CALCULATE(
    COUNT(master_orders[review_score]),
    master_orders[review_score] = 5
)
```

```dax
5-Star Rate = 
DIVIDE(
    [5-Star Reviews],
    COUNT(master_orders[review_score]),
    0
)
```

#### Time Intelligence
```dax
Revenue Previous Month = 
CALCULATE(
    [Total Revenue],
    DATEADD(master_orders[order_purchase_timestamp], -1, MONTH)
)
```

```dax
Revenue Growth % = 
DIVIDE(
    [Total Revenue] - [Revenue Previous Month],
    [Revenue Previous Month],
    0
)
```

```dax
YTD Revenue = 
TOTALYTD(
    [Total Revenue],
    master_orders[order_purchase_timestamp]
)
```

---

### 4. Create Visualizations

#### Page 1: Executive Dashboard

**KPI Cards (Top Row):**
1. Card: Total Revenue
2. Card: Total Orders
3. Card: Total Customers
4. Card: Average Order Value
5. Card: Average Review Score

**Charts:**
1. **Line Chart:** Revenue by Month
   - X-axis: `order_purchase_timestamp` (Month)
   - Y-axis: `Total Revenue`
   
2. **Column Chart:** Orders by Month
   - X-axis: `order_purchase_timestamp` (Month)
   - Y-axis: `Total Orders`

3. **Pie Chart:** Order Status Distribution
   - Legend: `order_status`
   - Values: `Total Orders`

4. **Gauge:** Late Delivery Rate
   - Value: `Late Delivery Rate`
   - Target: 0.05 (5%)

---

#### Page 2: Product Performance

1. **Bar Chart:** Top 10 Categories by Revenue
   - Y-axis: `product_category_name`
   - X-axis: `Total Revenue`
   - Filter: Top 10

2. **Treemap:** Category Revenue Distribution
   - Group: `product_category_name`
   - Values: `Total Revenue`

3. **Scatter Plot:** Revenue vs Orders
   - X-axis: `Total Orders`
   - Y-axis: `Total Revenue`
   - Legend: `product_category_name`

---

#### Page 3: Customer Analysis

1. **Pie Chart:** Customer Segments
   - Create calculated column first:
   ```dax
   Customer Segment = 
   VAR OrderCount = 
       CALCULATE(
           DISTINCTCOUNT(master_orders[order_id]),
           ALLEXCEPT(master_orders, master_orders[customer_unique_id])
       )
   RETURN
       SWITCH(
           TRUE(),
           OrderCount = 1, "One-time",
           OrderCount = 2, "Two-time",
           OrderCount >= 3, "3+ times"
       )
   ```
   - Legend: `Customer Segment`
   - Values: Count of customer_unique_id

2. **Map:** Revenue by State
   - Location: `customer_state`
   - Size: `Total Revenue`

3. **Bar Chart:** Top 10 States by Revenue
   - Y-axis: `customer_state`
   - X-axis: `Total Revenue`
   - Filter: Top 10

4. **Card:** Repeat Customer Rate

---

#### Page 4: Delivery Performance

1. **Histogram:** Delivery Delay Distribution
   - X-axis: `delivery_delay_days` (binned)
   - Y-axis: Count

2. **Donut Chart:** On-time vs Late
   - Legend: Create calculated column:
   ```dax
   Delivery Status = 
   IF(
       master_orders[delivery_delay_days] <= 0,
       "On-time/Early",
       "Late"
   )
   ```
   - Values: `Total Orders`

3. **Column Chart:** Review Score by Delivery Status
   - X-axis: `Delivery Status`
   - Y-axis: `Average Review Score`

4. **Table:** Delivery Performance by State
   - Columns: `customer_state`, `Total Orders`, `Late Delivery Rate`, `Average Delivery Days`

---

#### Page 5: Payment Analysis

1. **Pie Chart:** Payment Method Distribution
   - Legend: `payment_type`
   - Values: Count of payment records

2. **Column Chart:** Revenue by Payment Method
   - X-axis: `payment_type`
   - Y-axis: `Total Revenue`

3. **Line Chart:** Average Installments Trend
   - X-axis: Month
   - Y-axis: Average of `payment_installments`

---

### 5. Design Tips

#### Color Scheme:
Use consistent colors across all pages:
- Revenue: Blue (#2E86AB)
- Orders: Purple (#A23B72)
- Customers: Orange (#F18F01)
- Delivery: Green (#2A9D8F)
- Issues: Red (#E76F51)

#### Formatting:
1. **Currency:** Format all revenue as R$ with 2 decimals
2. **Percentages:** Format rates as % with 1 decimal
3. **Large Numbers:** Use K, M notation (e.g., R$ 1.5M)

#### Filters (Apply to all pages):
Add slicers for:
- Date range (order_purchase_timestamp)
- Order status
- Customer state

---

### 6. Interactive Features

#### Drill-through:
1. Create a detail page
2. Right-click any chart → Add drill-through
3. Users can click a category to see details

#### Tooltips:
1. Create a small tooltip page
2. Assign it to charts for hover details

#### Bookmarks:
1. Create bookmarks for different views
2. Add buttons to switch between them

---

## Quick Start Checklist

- [ ] Load `master_orders.csv` into Power BI
- [ ] Transform dates to Date/Time format
- [ ] Create all DAX measures (copy-paste from above)
- [ ] Create calculated columns (Customer Segment, Delivery Status)
- [ ] Build Page 1: Executive Dashboard
- [ ] Build Page 2: Product Performance
- [ ] Build Page 3: Customer Analysis
- [ ] Build Page 4: Delivery Performance
- [ ] Build Page 5: Payment Analysis
- [ ] Add slicers for date, state, order status
- [ ] Apply consistent color scheme
- [ ] Test all interactions
- [ ] Save as .pbix file

---

## Common Issues & Solutions

**Issue:** Dates showing as text
- **Fix:** Power Query → Change Type → Date/Time

**Issue:** Relationships not working
- **Fix:** Model view → Create relationship on `order_id`

**Issue:** Measures showing wrong numbers
- **Fix:** Check filter context - use CALCULATE when needed

**Issue:** Charts look crowded
- **Fix:** Use Top N filter or drill-down

**Issue:** Performance is slow
- **Fix:** Reduce date granularity or use summarized tables

---

## Export & Share

### Save Your Work:
1. **File** → **Save As** → `Olist_Dashboard.pbix`
2. Save in your `powerbi/` folder

### Export to PDF (for portfolio):
1. **File** → **Export to PDF**
2. Select all pages
3. Save as `Olist_Dashboard.pdf`

### Take Screenshots:
1. Use Windows Snipping Tool (Win + Shift + S)
2. Capture each dashboard page
3. Save in `reports/charts/powerbi_screenshots/`

### Share Online (Optional):
1. Publish to Power BI Service (requires Microsoft account)
2. Or use Power BI Report Server

---

## For Interviews

**What to say:**
> "I built an interactive Power BI dashboard with 5 pages analyzing revenue, products, customers, delivery, and payments. I used DAX for custom measures like repeat customer rate and late delivery percentage. The dashboard is fully interactive with slicers and drill-through capabilities."

**What to demo:**
1. Show Executive Dashboard (Page 1)
2. Click a category to drill into details
3. Use date slicer to show time-based trends
4. Show the insight: "96.8% one-time buyers"

---

## Need Help?

**Power BI Resources:**
- Official Docs: https://learn.microsoft.com/power-bi/
- DAX Guide: https://dax.guide/
- YouTube: Search "Power BI tutorial" by Guy in a Cube

**Tips:**
- Start simple, add complexity later
- Use the AI visuals (Q&A) feature
- Check "Show data points" on hover
- Always test with different filters
