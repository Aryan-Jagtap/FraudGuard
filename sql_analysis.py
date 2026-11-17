
from database import run_query

queries = {
    "1. High-risk transactions": """
        SELECT transaction_id, customer_id, amount,
               risk_score, triggered_rules
        FROM transactions
        WHERE risk_level = 'High'
        ORDER BY risk_score DESC
    """,

    "2. Rule-wise alert count": """
        SELECT
            SUM(R001) AS high_value_alerts,
            SUM(R002) AS velocity_alerts,
            SUM(R003) AS failed_attempt_alerts,
            SUM(R004) AS location_alerts,
            SUM(R005) AS unusual_spending_alerts
        FROM transactions
    """,

    "3. Customers with most alerts": """
        SELECT customer_id,
               COUNT(*) AS alert_count,
               ROUND(SUM(amount), 2) AS total_amount
        FROM transactions
        WHERE alert_status = 1
        GROUP BY customer_id
        ORDER BY alert_count DESC
        LIMIT 10
    """,

    "4. Alert distribution by risk": """
        SELECT risk_level, COUNT(*) AS total
        FROM transactions
        WHERE alert_status = 1
        GROUP BY risk_level
    """
}

for title, query in queries.items():
    print(f"\n{'=' * 55}")
    print(title)
    print('=' * 55)
    print(run_query(query).to_string(index=False))
