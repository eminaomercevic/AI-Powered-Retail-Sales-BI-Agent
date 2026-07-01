-- 1. Main KPI Summary
SELECT 
    ROUND(SUM(total_amount), 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders,
    COUNT(DISTINCT customer_key) AS total_customers,
    ROUND(SUM(total_amount) / COUNT(DISTINCT invoice_no), 2) AS average_order_value
FROM fact_sales;

-- 2. Monthly Revenue
SELECT 
    d.year,
    d.month,
    ROUND(SUM(f.total_amount), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. Top Products by Revenue

SELECT 
    p.description,
    ROUND(SUM(f.total_amount), 2) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.description
ORDER BY revenue DESC
LIMIT 10;

-- 4. Sales by Country

SELECT 
    c.country,
    ROUND(SUM(f.total_amount), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.country
ORDER BY revenue DESC
LIMIT 10;

-- 5. Top Customers by Revenue

SELECT 
    c.customer_id,
    c.country,
    ROUND(SUM(f.total_amount), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.country
ORDER BY revenue DESC
LIMIT 10;