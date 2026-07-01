"""
Validation checks for the Online Retail II warehouse.

Purpose:
- Verify that the cleaned raw CSV and Supabase warehouse contain matching totals.
- Support the evaluation loop required for the final BI project.

Run from the project root or adjust CSV_PATH as needed.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv("agent/.env")

CSV_PATH = "data/online_retail_II.csv"

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})


def clean_raw_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="ISO-8859-1")
    df = df.rename(columns={
        "Invoice": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "Price": "unit_price",
        "Customer ID": "customer_id",
        "Country": "country",
    })

    df = df.dropna(subset=["description", "customer_id"])
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]
    df = df[~df["invoice_no"].astype(str).str.startswith("C")]
    df["total_amount"] = df["quantity"] * df["unit_price"]
    return df


def main():
    print("Running validation checks...")

    cleaned = clean_raw_csv(CSV_PATH)
    raw_cleaned_rows = len(cleaned)
    raw_cleaned_revenue = round(cleaned["total_amount"].sum(), 2)

    warehouse_counts = pd.read_sql(
        text("SELECT COUNT(*) AS fact_rows, ROUND(SUM(total_amount), 2) AS warehouse_revenue FROM fact_sales"),
        engine,
    )

    warehouse_rows = int(warehouse_counts.loc[0, "fact_rows"])
    warehouse_revenue = float(warehouse_counts.loc[0, "warehouse_revenue"])

    print(f"Cleaned CSV rows: {raw_cleaned_rows}")
    print(f"Warehouse fact_sales rows: {warehouse_rows}")
    print(f"Cleaned CSV revenue: {raw_cleaned_revenue}")
    print(f"Warehouse revenue: {warehouse_revenue}")

    assert raw_cleaned_rows == warehouse_rows, "Row count mismatch between cleaned CSV and warehouse."
    assert abs(raw_cleaned_revenue - warehouse_revenue) < 0.01, "Revenue mismatch between cleaned CSV and warehouse."

    print("Validation passed: cleaned CSV totals match warehouse totals.")


if __name__ == "__main__":
    main()
