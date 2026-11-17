
import pandas as pd

RULES = {
    "R001": {"name": "High Value Transaction", "score": 30},
    "R002": {"name": "High Transaction Velocity", "score": 40},
    "R003": {"name": "Multiple Failed Attempts", "score": 35},
    "R004": {"name": "Unusual Location with High Amount", "score": 25},
    "R005": {"name": "Unusual Customer Spending", "score": 30}
}


def evaluate_transactions(df):

    required_columns = [
        "transaction_id",
        "customer_id",
        "amount",
        "timestamp",
        "location",
        "home_location",
        "failed_attempts"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="raise"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="raise"
    )

    if (df["amount"] < 0).any():
        raise ValueError("Transaction amounts cannot be negative.")

    df["failed_attempts"] = pd.to_numeric(
        df["failed_attempts"],
        errors="raise"
    )

    if df["failed_attempts"].isna().any():
        raise ValueError("Failed attempts cannot contain missing values.")

    df = df.sort_values(
        ["customer_id", "timestamp"]
    ).reset_index(drop=True)

    # R001: High-value transaction
    df["R001"] = (
        df["amount"] > 50000
    ).astype(int)

    # R002: More than 3 transactions within 60 seconds
    df["R002"] = 0

    for customer_id, indexes in df.groupby("customer_id").groups.items():

        customer_rows = df.loc[indexes].sort_values("timestamp")

        times = customer_rows.set_index("timestamp")

        rolling_count = (
            pd.Series(1, index=times.index)
            .rolling("60s", closed="both")
            .sum()
        )

        triggered = rolling_count > 3

        df.loc[customer_rows.index, "R002"] = (
            triggered.astype(int).values
        )

    # R003: Multiple failed attempts
    df["R003"] = (
        df["failed_attempts"] >= 3
    ).astype(int)

    # R004: Location mismatch AND transaction amount > 20,000
    location_mismatch = (
        df["location"].astype(str).str.strip().str.lower()
        !=
        df["home_location"].astype(str).str.strip().str.lower()
    )

    df["R004"] = (
        location_mismatch & (df["amount"] > 20000)
    ).astype(int)

    # R005: Unusual customer spending AND amount > 20,000
    customer_median = df.groupby(
        "customer_id"
    )["amount"].transform("median")

    unusual_spending = (
        df["amount"] > (customer_median * 3)
    )

    df["R005"] = (
        unusual_spending & (df["amount"] > 20000)
    ).astype(int)

    # Calculate combined risk score
    rule_columns = list(RULES.keys())

    df["risk_score"] = sum(
        df[rule] * RULES[rule]["score"]
        for rule in rule_columns
    )

    df["risk_score"] = df["risk_score"].clip(upper=100)

    # Record triggered rules
    df["triggered_rules"] = df[rule_columns].apply(
        lambda row: ", ".join(
            rule for rule in rule_columns
            if row[rule] == 1
        ) or "None",
        axis=1
    )

    # Assign risk category
    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 0, 29, 59, 100],
        labels=["Legitimate", "Low", "Medium", "High"]
    ).astype(str)

    df["alert_status"] = (
        df["risk_score"] > 0
    ).astype(int)

    return df


if __name__ == "__main__":

    input_file = "data/transactions.csv"
    output_file = "data/analyzed_transactions.csv"

    transactions = pd.read_csv(input_file)

    analyzed = evaluate_transactions(transactions)

    analyzed.to_csv(output_file, index=False)

    print("FraudGuard rule engine executed successfully.")
    print(f"Transactions analyzed: {len(analyzed)}")
    print(f"Alerts generated: {analyzed['alert_status'].sum()}")

    print("\nRisk distribution:")
    print(analyzed["risk_level"].value_counts())

    print("\nRule-wise alert counts:")
    print(analyzed[rule_columns].sum() if False else analyzed[list(RULES.keys())].sum())
