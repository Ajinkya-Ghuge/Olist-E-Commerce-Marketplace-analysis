# Power BI Dashboard - Quick Start

## 🎯 The Easiest Way

### Option 1: Use Master Orders CSV (RECOMMENDED!)

1. **Open Power BI Desktop** (free download from Microsoft)
2. **Get Data** → **Text/CSV**
3. **Load:** `data/processed/master_orders.csv`
4. **Done!** You have all data in one table

### Option 2: Connect to SQLite Database

1. **Get Data** → **ODBC**
2. Point to `data/olist_analytics.db`
3. Requires SQLite ODBC driver (free but extra step)

---

## 📊 What You'll Build

5 Dashboard Pages:
1. **Executive Summary** - KPIs and overview
2. **Product Performance** - Categories and top products
3. **Customer Analysis** - Retention and geography
4. **Delivery Performance** - On-time vs late
5. **Payment Analysis** - Methods and installments

---

## 🚀 Step-by-Step

### Step 1: Load Data (5 minutes)
1. Open Power BI Desktop
2. Get Data → Text/CSV
3. Select `data/processed/master_orders.csv`
4. Click **Transform Data**
5. Set date columns to Date/Time type
6. Click **Close & Apply**

### Step 2: Create Measures (10 minutes)
Copy-paste DAX formulas from `POWERBI_GUIDE.md`:
- Total Revenue
- Total Orders
- Average Order Value
- Repeat Customer Rate
- Late Delivery Rate
- Average Review Score

### Step 3: Build Dashboards (30 minutes)
Follow the visual guide in `POWERBI_GUIDE.md`:
- Add KPI cards
- Create charts
- Add slicers
- Apply formatting

---

## 📋 Files You Need

**Input Data:**
- ✅ `data/processed/master_orders.csv` - Main table (use this!)

**OR if you want separate tables:**
- `data/processed/orders_cleaned.csv`
- `data/processed/order_items_cleaned.csv`
- `data/processed/customers_cleaned.csv`
- `data/processed/products_cleaned.csv`
- `data/processed/payments_cleaned.csv`
- `data/processed/reviews_cleaned.csv`

**Reference:**
- `powerbi/POWERBI_GUIDE.md` - Complete instructions with DAX formulas

---

## 🎨 Dashboard Preview

### Page 1: Executive Dashboard
```
┌─────────────────────────────────────────────────────┐
│  R$ 15.9M      99K Orders    96K Customers   4.16/5 │
│  Revenue        Orders        Customers      Score  │
├─────────────────────────────────────────────────────┤
│  📈 Revenue Trend          📊 Order Volume          │
│                                                      │
├──────────────────────┬──────────────────────────────┤
│  🎯 Order Status     │  ⚠️  Late Delivery Rate     │
│  (Pie Chart)         │  (Gauge: 6.8%)              │
└──────────────────────┴──────────────────────────────┘
```

### Page 2: Product Performance
- Top 10 categories bar chart
- Category treemap
- Revenue vs orders scatter plot

### Page 3: Customer Analysis
- One-time vs repeat (pie: 96.8% one-time!)
- Revenue by state (map)
- Top 10 states bar chart

### Page 4: Delivery Performance
- Delay distribution histogram
- On-time vs late donut (93.2% on-time)
- Review score by delivery status

### Page 5: Payment Analysis
- Payment method distribution
- Revenue by payment type
- Installments trend

---

## 💡 Key Insights to Show

When presenting your dashboard, highlight:

1. **"96.8% One-Time Buyers"**
   - Show pie chart on Customer Analysis page
   - Explain the retention problem

2. **"Late Deliveries Tank Satisfaction"**
   - Show delivery performance page
   - Point out 2-point drop in review scores

3. **"R$ 15.9M Revenue, R$ 159 AOV"**
   - Executive dashboard KPIs
   - Show monthly trend

4. **"Top 3 Categories: R$ 3M+"**
   - Product performance page
   - Show treemap

---

## 🎤 For Interviews

### Demo Flow (2 minutes):
1. **Start:** Executive Dashboard
   - "Here's the overall business performance"
   - Point to key KPIs

2. **Click:** Customer Analysis
   - "The biggest problem: 96.8% one-time buyers"
   - Show pie chart

3. **Use Slicer:** Filter by date range
   - "Dashboard is fully interactive"
   - Show how numbers change

4. **Click:** Delivery Performance
   - "Late deliveries destroy satisfaction"
   - Show bar chart comparison

5. **Conclude:** Product Performance
   - "These top categories drive the business"
   - Show recommendations

### What to Say:
> "I built an interactive Power BI dashboard connecting to cleaned data from my Python pipeline. It has 5 pages with 20+ visuals covering revenue, products, customers, delivery, and payments. I used DAX for calculated measures like repeat customer rate and delivery performance. The key insight: 96.8% one-time buyers represents a huge growth opportunity."

---

## ⚠️ Common Mistakes to Avoid

1. **Don't use RAW data** - Use the cleaned `master_orders.csv`
2. **Don't skip date formatting** - Always set proper Date/Time type
3. **Don't forget relationships** - If using multiple tables, link on order_id
4. **Don't ignore filters** - Test all slicers work correctly
5. **Don't overcrowd** - Keep visuals clean and focused

---

## 📸 Save Your Work

### For Your Portfolio:
1. **Save PBIX:** `Olist_Dashboard.pbix`
2. **Export PDF:** File → Export to PDF
3. **Take Screenshots:** Use Snipping Tool
4. **Save in:** `reports/charts/powerbi_screenshots/`

### For GitHub:
- Upload screenshots (PNG)
- Don't upload .pbix (too large)
- Include dashboard preview in README

---

## ✅ Quick Checklist

Dashboard Creation:
- [ ] Downloaded Power BI Desktop
- [ ] Loaded master_orders.csv
- [ ] Fixed date column types
- [ ] Created all DAX measures
- [ ] Built Executive Dashboard page
- [ ] Built Product Performance page
- [ ] Built Customer Analysis page
- [ ] Built Delivery Performance page
- [ ] Built Payment Analysis page
- [ ] Added slicers (date, state, status)
- [ ] Applied consistent colors
- [ ] Tested all interactions
- [ ] Saved as .pbix file
- [ ] Exported to PDF
- [ ] Took screenshots

Portfolio:
- [ ] Screenshots saved in reports/
- [ ] Can demo dashboard in 2 minutes
- [ ] Know how to explain key insights
- [ ] Prepared for DAX questions
- [ ] Ready to show in interviews

---

## 🆘 Need Help?

**Issue:** Power BI not installed
- Download free: https://powerbi.microsoft.com/desktop/

**Issue:** CSV won't load
- Check file path is correct
- Try "Get Data" → "Folder" → navigate to folder

**Issue:** Dates showing wrong
- Power Query → Select column → Change Type → Date/Time

**Issue:** Visuals not working
- Check measure formulas
- Verify column names match exactly

**Issue:** Dashboard is slow
- Reduce data range using slicer
- Simplify visuals
- Use summarized data

---

**Ready to impress recruiters with your Power BI skills!** 📊✨
