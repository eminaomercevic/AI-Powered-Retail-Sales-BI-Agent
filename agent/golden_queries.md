# Golden Queries

## 1. Main KPI Summary
Question: What are the total revenue, total orders, total customers, and average order value?

Expected SQL:
SELECT 
    ROUND(SUM(total_amount), 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders,
    COUNT(DISTINCT customer_key) AS total_customers,
    ROUND(SUM(total_amount) / COUNT(DISTINCT invoice_no), 2) AS average_order_value
FROM fact_sales;

## 2. Monthly Revenue
Question: Show revenue by year and month.

Expected SQL:
SELECT 
    d.year,
    d.month,
    ROUND(SUM(f.total_amount), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

## 3. Top Products by Revenue
Question: What are the top 10 products by revenue?

Expected SQL:
SELECT 
    p.description,
    ROUND(SUM(f.total_amount), 2) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.description
ORDER BY revenue DESC
LIMIT 10;

## 4. Sales by Country
Question: Which countries generate the most revenue?

Expected SQL:
SELECT 
    c.country,
    ROUND(SUM(f.total_amount), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.country
ORDER BY revenue DESC
LIMIT 10;

## 5. Top Customers by Revenue
Question: Who are the top customers by revenue?

Expected SQL:
SELECT 
    c.customer_id,
    c.country,
    ROUND(SUM(f.total_amount), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.country
ORDER BY revenue DESC
LIMIT 10;