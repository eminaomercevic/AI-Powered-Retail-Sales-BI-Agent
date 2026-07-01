import os
import re
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MCP_URL = "http://127.0.0.1:8000"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)


def get_schema():
    response = requests.get(f"{MCP_URL}/schema")
    response.raise_for_status()
    return response.json()


def run_sql(sql):
    response = requests.post(
        f"{MCP_URL}/query",
        json={"sql": sql}
    )
    response.raise_for_status()
    return response.json()


def load_system_prompt():
    with open("system_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


def clean_sql(model_output):
    text = model_output.strip()

    # Remove markdown code fences if the model accidentally returns them.
    text = re.sub(r"^```sql", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    return text


def validate_agent_output(sql):
    lowered = sql.strip().lower()

    if sql.startswith("REFUSED:"):
        return sql

    if sql.startswith("CLARIFICATION_NEEDED:"):
        return sql

    if not lowered.startswith("select"):
        return "REFUSED: Only safe SELECT queries are allowed."

    dangerous_keywords = [
        "insert", "update", "delete", "drop", "alter",
        "truncate", "create", "grant", "revoke"
    ]

    for keyword in dangerous_keywords:
        if re.search(rf"\b{keyword}\b", lowered):
            return "REFUSED: Only safe SELECT queries are allowed."

    return sql


def generate_sql_with_llm(question, schema):
    system_prompt = load_system_prompt()

    prompt = f"""
{system_prompt}

Schema context from MCP server:
{schema}

User question:
{question}

Return only the SQL query or one of the exact refusal/clarification messages.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
        ),
    )

    sql = clean_sql(response.text)
    sql = validate_agent_output(sql)

    return sql


def print_result(result):
    rows = result.get("rows", [])

    if not rows:
        print("No rows returned.")
        return

    for row in rows:
        print(row)


def main():
    print("Retail BI LLM Agent")
    print("Ask a question about sales, products, customers, dates, or countries.")
    print("Type 'exit' to stop.\n")

    schema = get_schema()
    print("Connected to MCP server.")
    print("Schema loaded from MCP server.")
    print("Available tables:", ", ".join([key for key in schema.keys() if key != "relationships"]))

    while True:
        question = input("\nQuestion: ")

        if question.lower() == "exit":
            break

        sql = generate_sql_with_llm(question, schema)

        print("\nAgent output:")
        print(sql)

        if sql.startswith("REFUSED:") or sql.startswith("CLARIFICATION_NEEDED:"):
            continue

        try:
            result = run_sql(sql)
            print("\nResult:")
            print_result(result)
        except Exception as e:
            print("\nError running query:")
            print(e)


if __name__ == "__main__":
    main()