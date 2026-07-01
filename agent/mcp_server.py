import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

app = FastAPI(title="Retail BI MCP Server")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)


class QueryRequest(BaseModel):
    sql: str


def validate_sql(sql: str):
    dangerous_keywords = [
        "insert", "update", "delete", "drop", "alter",
        "truncate", "create", "grant", "revoke"
    ]

    cleaned = sql.strip().lower()

    if not cleaned.startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")

    for keyword in dangerous_keywords:
        if keyword in cleaned:
            raise HTTPException(
                status_code=400,
                detail=f"Dangerous SQL keyword detected: {keyword}"
            )


@app.get("/")
def home():
    return {"message": "Retail BI MCP Server is running"}


@app.get("/schema")
def get_schema():
    return {
        "fact_sales": [
            "sales_key",
            "invoice_no",
            "date_key",
            "product_key",
            "customer_key",
            "quantity",
            "unit_price",
            "total_amount"
        ],
        "dim_date": [
            "date_key",
            "full_date",
            "year",
            "month",
            "day",
            "hour",
            "day_of_week"
        ],
        "dim_product": [
            "product_key",
            "stock_code",
            "description"
        ],
        "dim_customer": [
            "customer_key",
            "customer_id",
            "country"
        ],
        "relationships": [
            "fact_sales.date_key = dim_date.date_key",
            "fact_sales.product_key = dim_product.product_key",
            "fact_sales.customer_key = dim_customer.customer_key"
        ]
    }


@app.post("/query")
def run_query(request: QueryRequest):
    validate_sql(request.sql)

    try:
        df = pd.read_sql(text(request.sql), engine)
        return {
            "columns": df.columns.tolist(),
            "rows": df.head(50).to_dict(orient="records"),
            "row_count_returned": len(df.head(50))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))