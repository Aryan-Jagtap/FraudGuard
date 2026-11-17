
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "database/fraudguard.db"
CSV_PATH = "data/analyzed_transactions.csv"


def save_transactions():
    """Save analyzed transactions into the SQLite database."""

    Path("database").mkdir(exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    connection = sqlite3.connect(DB_PATH)

    df.to_sql(
        "transactions",
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()

    print(f"Successfully saved {len(df)} transactions to SQLite.")


def run_query(query):
    """Execute a SQL query and return its results."""

    connection = sqlite3.connect(DB_PATH)

    result = pd.read_sql_query(query, connection)

    connection.close()

    return result


if __name__ == "__main__":
    save_transactions()

    print("\nTotal transactions:")
    print(run_query("SELECT COUNT(*) AS total FROM transactions"))

    print("\nRisk level distribution:")
    print(run_query("""
        SELECT risk_level, COUNT(*) AS transaction_count
        FROM transactions
        GROUP BY risk_level
        ORDER BY transaction_count DESC
    """))
