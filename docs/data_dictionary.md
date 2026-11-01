# Olist Analytics Pro - Data Dictionary

**Last Updated:** 2026-10-20  
**Data Source:** Brazilian Olist E-Commerce Dataset  
**Analysis Period:** 2016-09-04 to 2018-10-17

---

## Dataset Overview

The Olist dataset contains information about **99,441 orders** made at multiple marketplaces in Brazil between September 2016 and October 2018. The dataset consists of **9 interconnected CSV files** representing different aspects of the e-commerce marketplace.

**Total Records Across All Files:** 1,550,862  
**Total File Size:** ~200 MB

---

## Table Relationships

```
customers ──(1:1)── orders ──(1:M)── order_items ──(M:1)── products
                        │                  │
                        │                  └──(M:1)── sellers
                        │
                        ├──(1:M)── payments
                        │
                        └──(1:1)── reviews

geolocation: Supporting reference table for zip codes
product_category_name_translation: Translation table for categories
```

---

## File Descriptions

### 1. olist_customers_dataset.csv
**Records:** 99,441  
**Grain:** One row per customer  
**Primary Key:** `customer_id`

Contains customer demographic and location information.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| customer_id | object | 0 | Unique identifier for customer (used in orders) |
| customer_unique_id | object | 0 | Real-world unique customer identifier (3,345 duplicates indicate returning customers) |
| customer_zip_code_prefix | int64 | 0 | First 5 digits of customer zip code |
| customer_city | object | 0 | Customer city name |
| customer_state | object | 0 | Customer state (2-letter code) |

**Data Quality Notes:**
- ⚠️ **customer_unique_id has 3,345 duplicates** - This is expected behavior indicating customers who made multiple orders
- ✅ customer_id is unique and suitable as primary key

---

### 2. olist_orders_dataset.csv
**Records:** 99,441  
**Grain:** One row per order  
**Primary Key:** `order_id`  
**Foreign Key:** `customer_id` → customers

Contains order-level information and status tracking.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| order_id | object | 0 | Unique order identifier |
| customer_id | object | 0 | Foreign key to customers table |
| order_status | object | 0 | Current order status (delivered, shipped, canceled, etc.) |
| order_purchase_timestamp | object | 0 | When the order was created (2016-09-04 to 2018-10-17) |
| order_approved_at | object | 160 (0.16%) | When payment was approved |
| order_delivered_carrier_date | object | 1,783 (1.79%) | When order was handed to logistics partner |
| order_delivered_customer_date | object | 2,965 (2.98%) | Actual customer delivery date |
| order_estimated_delivery_date | object | 0 | Promised delivery date (2016-09-30 to 2018-11-12) |

**Data Quality Notes:**
- ⚠️ **Missing delivery dates** - 2,965 orders (2.98%) missing actual delivery date (likely canceled/processing)
- ⚠️ **Missing carrier dates** - 1,783 orders (1.79%) not yet handed to carrier
- ⚠️ **Missing approval dates** - 160 orders (0.16%) awaiting payment approval
- ✅ order_id and customer_id are both unique (1:1 relationship in this dataset)

---

### 3. olist_order_items_dataset.csv
**Records:** 112,650  
**Grain:** One row per item within an order  
**Composite Key:** `order_id` + `order_item_id`  
**Foreign Keys:** `order_id` → orders, `product_id` → products, `seller_id` → sellers

Contains individual line items for each order.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| order_id | object | 0 | Foreign key to orders table |
| order_item_id | int64 | 0 | Sequential item number within the order (1, 2, 3...) |
| product_id | object | 0 | Foreign key to products table |
| seller_id | object | 0 | Foreign key to sellers table |
| shipping_limit_date | object | 0 | Latest date seller should ship item (2016-09-19 to 2020-04-09) |
| price | float64 | 0 | Item price (BRL): min=0.85, max=6,735.00, mean=120.65 |
| freight_value | float64 | 0 | Shipping cost (BRL): min=0.00, max=409.68, mean=19.99 |

**Data Quality Notes:**
- ✅ No missing values
- ✅ No duplicate rows
- ℹ️ **112,650 items across 98,666 orders** = ~1.14 items per order average
- ⚠️ **Multiple items per order** - 13,984 orders (12.4%) contain multiple items
- ⚠️ **Price of 0.85 BRL** - Investigate lowest-priced items

**Important Calculations:**
- **Order Item Total** = price + freight_value
- **Order Total** = SUM(price + freight_value) for all items in an order

---

### 4. olist_order_payments_dataset.csv
**Records:** 103,886  
**Grain:** One row per payment transaction  
**Foreign Key:** `order_id` → orders

Contains payment method and installment information. Note: An order can have multiple payment methods.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| order_id | object | 0 | Foreign key to orders table |
| payment_sequential | int64 | 0 | Sequential payment number for multi-payment orders |
| payment_type | object | 0 | Method of payment (credit_card, boleto, voucher, debit_card) |
| payment_installments | int64 | 0 | Number of installments |
| payment_value | float64 | 0 | Payment amount (BRL): min=0.00, max=13,664.08, mean=154.10 |

**Data Quality Notes:**
- ⚠️ **103,886 payments for 99,441 orders** - 4,446 orders (4.28%) have multiple payments
- ⚠️ **Payment values may not match order item totals** - Requires reconciliation analysis
- ⚠️ **Zero-value payments** - Investigate why some payments are 0.00

**Important Calculations:**
- **Order Payment Total** = SUM(payment_value) for all payments in an order
- **Reconciliation Required:** Compare order_items total vs payments total

---

### 5. olist_order_reviews_dataset.csv
**Records:** 99,224  
**Grain:** One row per review (most orders have one review)  
**Foreign Key:** `order_id` → orders

Contains customer satisfaction ratings and comments.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| review_id | object | 0 | Unique review identifier |
| order_id | object | 0 | Foreign key to orders table |
| review_score | int64 | 0 | Customer satisfaction rating (1-5 scale) |
| review_comment_title | object | 87,656 (88.3%) | Optional review title |
| review_comment_message | object | 58,247 (58.7%) | Optional review text |
| review_creation_date | object | 0 | When review was created (2016-10-02 to 2018-08-31) |
| review_answer_timestamp | object | 0 | When review was answered (2016-10-07 to 2018-10-29) |

**Data Quality Notes:**
- ⚠️ **Missing review text** - 88.3% of reviews have no title, 58.7% have no message
- ⚠️ **99,224 reviews for 99,441 orders** - 217 orders have no review
- ⚠️ **551 orders have multiple reviews** (0.56%)
- ✅ Review scores are always present (mandatory field)

---

### 6. olist_products_dataset.csv
**Records:** 32,951  
**Grain:** One row per unique product  
**Primary Key:** `product_id`

Contains product characteristics and dimensions.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| product_id | object | 0 | Unique product identifier |
| product_category_name | object | 610 (1.85%) | Category name in Portuguese |
| product_name_lenght | float64 | 610 (1.85%) | Length of product name in characters |
| product_description_lenght | float64 | 610 (1.85%) | Length of product description |
| product_photos_qty | float64 | 610 (1.85%) | Number of product photos |
| product_weight_g | float64 | 2 (0.01%) | Product weight in grams |
| product_length_cm | float64 | 2 (0.01%) | Product package length |
| product_height_cm | float64 | 2 (0.01%) | Product package height |
| product_width_cm | float64 | 2 (0.01%) | Product package width |

**Data Quality Notes:**
- ⚠️ **610 products (1.85%) missing category** - All metadata missing for these products
- ⚠️ **2 products missing dimensions** - Nearly complete dimension data
- ℹ️ **32,951 unique products** sold through **3,095 sellers**

---

### 7. olist_sellers_dataset.csv
**Records:** 3,095  
**Grain:** One row per seller  
**Primary Key:** `seller_id`

Contains seller location information.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| seller_id | object | 0 | Unique seller identifier |
| seller_zip_code_prefix | int64 | 0 | First 5 digits of seller zip code |
| seller_city | object | 0 | Seller city name |
| seller_state | object | 0 | Seller state (2-letter code) |

**Data Quality Notes:**
- ✅ Complete data, no missing values
- ✅ All sellers have valid location information

---

### 8. olist_geolocation_dataset.csv
**Records:** 1,000,163  
**Grain:** One row per zip code prefix + geographic coordinate combination  
**Warning:** Not a dimension table - many-to-many relationship

Contains geographic coordinates for Brazilian zip codes.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| geolocation_zip_code_prefix | int64 | 0 | First 5 digits of zip code |
| geolocation_lat | float64 | 0 | Latitude |
| geolocation_lng | float64 | 0 | Longitude |
| geolocation_city | object | 0 | City name |
| geolocation_state | object | 0 | State (2-letter code) |

**Data Quality Notes:**
- ⚠️ **261,831 duplicate rows (26.2%)** - Multiple coordinates per zip code
- ⚠️ **NOT a dimension table** - One zip code can map to multiple lat/lng pairs
- ⚠️ **Use with caution** - May need aggregation or deduplication for joins

**Usage Recommendation:**
- For basic location analysis, use city/state from customers/sellers tables
- Use geolocation only if precise coordinates needed
- Consider aggregating (e.g., AVG lat/lng by zip code) before joining

---

### 9. product_category_name_translation.csv
**Records:** 71  
**Grain:** One row per product category  
**Primary Key:** `product_category_name`

Translates Portuguese category names to English.

| Column | Data Type | Nulls | Description |
|--------|-----------|-------|-------------|
| product_category_name | object | 0 | Category name in Portuguese (matches products table) |
| product_category_name_english | object | 0 | Category name in English |

**Data Quality Notes:**
- ✅ Complete translation data
- ℹ️ 71 product categories available

---

## Key Business Metrics Definitions

### Revenue Metrics
- **Gross Merchandise Value (GMV):** SUM(order_items.price)
- **Total Freight:** SUM(order_items.freight_value)
- **Total Order Value:** GMV + Total Freight
- **Payment Value:** SUM(payments.payment_value)
- ⚠️ **Important:** GMV ≠ Payment Value (requires reconciliation)

### Order Metrics
- **Total Orders:** COUNT(DISTINCT orders.order_id)
- **Total Order Items:** COUNT(order_items)
- **Average Items per Order:** Total Order Items / Total Orders
- **Average Order Value (AOV):** Total Order Value / Total Orders

### Customer Metrics
- **Total Customers:** COUNT(DISTINCT customers.customer_unique_id)
- **Total Customer IDs:** COUNT(DISTINCT customers.customer_id)
- **Repeat Customers:** Customers with multiple orders (customer_unique_id appears >1 time)
- **Customer Lifetime Orders:** COUNT orders per customer_unique_id

### Delivery Metrics
- **Estimated Delivery Time:** order_estimated_delivery_date - order_purchase_timestamp
- **Actual Delivery Time:** order_delivered_customer_date - order_purchase_timestamp
- **Delivery Delay:** order_delivered_customer_date - order_estimated_delivery_date
- **Late Delivery Rate:** % of orders where Delivery Delay > 0

### Satisfaction Metrics
- **Average Review Score:** AVG(review_score)
- **Review Distribution:** COUNT by review_score (1-5)
- **Review Rate:** COUNT(reviews) / COUNT(orders)

---

## Data Quality Summary

### ✅ Strengths
1. **Complete core data:** Orders, items, customers, sellers, products
2. **Valid primary keys:** order_id, customer_id, product_id, seller_id
3. **Rich time series:** 2+ years of transaction history
4. **Multi-dimensional:** Product, customer, seller, geographic attributes

### ⚠️ Quality Issues to Address
1. **Missing delivery dates:** 2.98% of orders (investigate order status)
2. **Missing product categories:** 1.85% of products
3. **Missing review comments:** 88% of reviews lack text
4. **Geolocation duplicates:** 26% duplicate rows (by design, needs careful handling)
5. **Payment reconciliation:** Payment totals may not match order item totals

### 🔍 Analytical Considerations
1. **Grain differences:** Orders (99k) ≠ Order Items (112k) ≠ Payments (103k)
2. **Join carefully:** Prevent row multiplication when joining order_items ↔ payments
3. **Missing reviews:** 217 orders have no review (0.2%)
4. **Multi-item orders:** 12.4% of orders contain multiple items
5. **Multi-payment orders:** 4.3% of orders have multiple payment transactions

---

## Next Phase Preview

**Phase 2: Data Quality and Cleaning**
- Investigate missing delivery dates by order_status
- Handle missing product categories
- Deduplicate geolocation table
- Reconcile payment amounts vs order totals
- Validate date logic (delivered > purchased, etc.)
- Document cleaning rules and transformations

---

**Generated:** 2026-10-20  
**Tool:** Python with Pandas  
**Analyst:** Portfolio Project
