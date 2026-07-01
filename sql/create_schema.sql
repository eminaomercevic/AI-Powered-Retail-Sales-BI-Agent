DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;

CREATE TABLE dim_date (
    date_key SERIAL PRIMARY KEY,
    full_date TIMESTAMP NOT NULL,
    year INT,
    month INT,
    day INT,
    hour INT,
    day_of_week VARCHAR(20)
);

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    stock_code VARCHAR(50) NOT NULL,
    description TEXT,
    CONSTRAINT unique_product UNIQUE (stock_code, description)
);

CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    country VARCHAR(100),
    CONSTRAINT unique_customer UNIQUE (customer_id, country)
);

CREATE TABLE fact_sales (
    sales_key SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50) NOT NULL,
    date_key INT NOT NULL,
    product_key INT NOT NULL,
    customer_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    CONSTRAINT fk_product FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    CONSTRAINT fk_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)
);