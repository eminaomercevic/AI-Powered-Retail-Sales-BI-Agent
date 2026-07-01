# AI-Powered Retail Sales BI Agent

Final exam project for IT 501 Business Intelligence.

## Project Overview

This project implements a Business Intelligence system for the Online Retail II dataset. It combines a Supabase PostgreSQL data warehouse, a Python CLI LLM Agent, a FastAPI MCP-style server, and Apache Superset dashboards.

The goal is to allow non-technical business users to ask natural-language questions about sales, products, customers, countries, and trends. The agent generates safe PostgreSQL SELECT queries, sends them to the MCP server, and retrieves results from the Supabase warehouse.

## Reference Repository

This project references the course BI Agent boilerplate repository:

https://github.com/dinokeco/bi-agent

The original repository demonstrates the Online Retail warehouse architecture and BI-agent workflow. This implementation adapts the same concept for the Online Retail II dataset, Supabase PostgreSQL, a custom Python CLI LLM Agent, a FastAPI MCP server, and Apache Superset dashboards.

## Dataset

- Dataset: Online Retail II
- Source: https://www.kaggle.com/datasets/tunguz/online-retail-ii
- Domain: E-commerce / retail transactions

The raw dataset should be placed locally at:

```text
data/online_retail_II.csv
```

The full CSV is not required in GitHub if file size or submission rules are a concern. The dataset source link is included for reproducibility.

## Data Warehouse Schema

The cleaned data is loaded into a star schema in Supabase PostgreSQL:

```text
dim_date
- date_key PK
- full_date
- year
- month
- day
- hour
- day_of_week

dim_product
- product_key PK
- stock_code
- description

dim_customer
- customer_key PK
- customer_id
- country

fact_sales
- sales_key PK
- invoice_no
- date_key FK -> dim_date.date_key
- product_key FK -> dim_product.product_key
- customer_key FK -> dim_customer.customer_key
- quantity
- unit_price
- total_amount
```

## Final Row Counts

```text
dim_date: 17,282
dim_product: 3,897
dim_customer: 4,346
fact_sales: 397,885
```

## Project Structure

```text
retail-bi-agent-final/
│
├── agent/
│   ├── bi_agent.py
│   ├── mcp_server.py
│   ├── system_prompt.txt
│   ├── golden_queries.md
│   ├── requirements.txt
│   └── .env                  # local only, do not upload
│
├── etl/
│   └── load_retail_data.ipynb
│
├── docs/
│   ├── screenshots/
│   ├── erd_star_schema.png
│   └── agent_mcp_architecture.png
│
├── data/
│   └── online_retail_II.csv  # optional/local only
│
├── validation_checks.py
├── README.md
└── .gitignore
```

## Should `load_retail_data.ipynb` be included?

Yes. Include `etl/load_retail_data.ipynb` because it documents the ETL process: reading the CSV, cleaning invalid records, creating dimensions, loading facts, and verifying row counts. This supports the data ingestion and validation requirements.

## Setup Instructions

### 1. Install Python dependencies

```bash
cd agent
python -m pip install -r requirements.txt
```

### 2. Configure environment variables

Create `agent/.env` locally:

```env
DB_USER=your_supabase_user
DB_PASSWORD=your_supabase_password
DB_HOST=your_supabase_host
DB_PORT=5432
DB_NAME=postgres
GEMINI_API_KEY=your_gemini_api_key
```

Do not upload `.env` to GitHub.

### 3. Start the MCP server

```bash
cd agent
python -m uvicorn mcp_server:app --reload
```

Test in browser:

```text
http://127.0.0.1:8000/schema
```

### 4. Run the BI Agent

In a second terminal:

```bash
cd agent
python bi_agent.py
```

Example questions:

```text
What is the total revenue?
Show monthly revenue by year and month.
Which 10 products generated the most revenue?
Which countries generate the most revenue?
Who are the top 10 customers by revenue?
Drop the fact_sales table.
```

The destructive query should be refused or blocked.

## MCP Server Endpoints

```text
GET  /schema
POST /query
```

`/schema` exposes the available tables, columns, and relationships.

`/query` executes only validated SELECT queries. Destructive SQL such as DROP, DELETE, ALTER, or UPDATE is blocked.

## Golden Queries

The project includes five Golden Queries in:

```text
agent/golden_queries.md
```

These are used to verify that the agent produces correct SQL for common BI questions.

## Superset Dashboards

Three dashboards were created:

1. Executive Overview
   - Total Revenue
   - Monthly Revenue Trend
   - Total Orders
   - Total Customers
   - Average Order Value

2. Product Performance
   - Top 10 Products by Revenue
   - Top 10 Products by Quantity Sold
   - Product Revenue Summary
   - Total Products

3. Customer & Country Analysis / Trend Monitor
   - Top Countries by Revenue
   - Customers by Country
   - Top Customers by Revenue
   - Monthly Revenue by Top Countries

## Key Business Metrics

- Total Revenue = SUM(total_amount)
- Total Orders = COUNT(DISTINCT invoice_no)
- Total Customers = COUNT(DISTINCT customer_id)
- Average Order Value = SUM(total_amount) / COUNT(DISTINCT invoice_no)
- Product Revenue = SUM(total_amount) grouped by product
- Quantity Sold = SUM(quantity)
- Country Revenue = SUM(total_amount) grouped by country

## Safety and Error Handling

The system has two safety layers:

1. Agent-level validation: the agent refuses destructive requests.
2. MCP-level validation: the MCP server blocks all non-SELECT SQL.

Example blocked query:

```sql
DROP TABLE fact_sales;
```

Expected response:

```text
Only SELECT queries are allowed.
```

## Notes for Submission

Do not upload:

```text
.env
.env*
__pycache__/
*.pyc
.ipynb_checkpoints/
```

Recommended to upload:

```text
README.md
agent/bi_agent.py
agent/mcp_server.py
agent/system_prompt.txt
agent/golden_queries.md
agent/requirements.txt
etl/load_retail_data.ipynb
validation_checks.py
docs/screenshots/
```
