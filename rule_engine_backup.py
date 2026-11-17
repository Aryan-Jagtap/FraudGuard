
import pandas as pd


# =====================================================
# 1. CONFIGURABLE FRAUD DETECTION RULES
# =====================================================

RULES = {
    "R001": {
        "name": "High Value Transaction",
        "threshold": 50000,
        "risk_points": 30
    },
    "R002": {
        "name": "High Transaction Velocity",
        "threshold": 3,
        "risk_points": 40
    },
    "R003": {
        "name": "Multiple Failed Attempts",
        "threshold": 3,
        "risk_points": 35
    },
    "R004": {
        "name": "Unusual Transaction Location",
        "risk_points": 25
    },
    "R005": {
        "name": "Unusual Spending Pattern",
        "threshold": 3,
        "risk_points": 30
    }
}


# =====================================================
# 2. FRAUD DETECTION FUNCTION
# =====================================================

def evaluate_transactions(df):

    df = df.copy()

    # Validate required columns
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
        col for col in required_columns if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert data types
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["amount"] = pd.to_numeric(df["amount"], errors="raise")
    df["failed_attempts"] = pd.to_numeric(
        df["failed_attempts"], errors="raise"
    )

    if (df["amount"] < 0).any():
        raise ValueError("Transaction amounts cannot be negative.")

    # Sort transactions by customer and timestamp
    df = df.sort_values(
        ["customer_id", "timestamp", "transaction_id"]
    ).reset_index(drop=True)

    # =================================================
    # R001: HIGH VALUE TRANSACTION
    # =================================================

    df["R001"] = (
        df["amount"] > RULES["R001"]["threshold"]
    )

    # =================================================
    # R002: HIGH TRANSACTION VELOCITY
    # More than 3 transactions in a rolling 60 seconds
    # =================================================

    velocity_flags = pd.Series(False, index=df.index)

    for customer, group in df.groupby("customer_id"):

        times = group["timestamp"]

        counts = (
            pd.Series(1, index=times)
            .rolling("60s", closed="both")
            .sum()
        )

        velocity_flags.loc[group.index] = (
            counts.to_numpy() > RULES["R002"]["threshold"]
        )

    df["R002"] = velocity_flags

    # =================================================
    # R003: MULTIPLE FAILED ATTEMPTS
    # =================================================

    df["R003"] = (
        df["failed_attempts"] >= RULES["R003"]["threshold"]
    )

    # =================================================
    # R004: UNUSUAL TRANSACTION LOCATION
    # =================================================

    df["R004"] = (
        df["location"].str.strip().str.lower()
        != df["home_location"].str.strip().str.lower()
    )

    # =================================================
    # R005: UNUSUAL SPENDING PATTERN
    # Use median customer spending as baseline
    # =================================================

    customer_median = (
        df.groupby("customer_id")["amount"]
        .transform("median")
    )

    df["R005"] = (
        df["amount"]
        > customer_median * RULES["R005"]["threshold"]
    )

    # =================================================
    # 3. RISK SCORE CALCULATION
    # =================================================

    rule_columns = list(RULES.keys())

    df["risk_score"] = 0

    for rule_id in rule_columns:

        df["risk_score"] += (
            df[rule_id].astype(int)
            * RULES[rule_id]["risk_points"]
        )

    # Cap risk score at 100
    df["risk_score"] = df["risk_score"].clip(upper=100)

    # =================================================
    # 4. IDENTIFY TRIGGERED RULES
    # =================================================

    df["triggered_rules"] = df[rule_columns].apply(
        lambda row: ", ".join(
            rule for rule in rule_columns if row[rule]
        ),
        axis=1
    )

    # =================================================
    # 5. FINAL RISK CLASSIFICATION
    # =================================================

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 0, 39, 69, 100],
        labels=[
            "Legitimate",
            "Low",
            "Medium",
            "High"
        ]
    ).astype(str)

    # Generate alert status
    df["alert_status"] = df["risk_score"] > 0

    return df


# =====================================================
# 6. RUN RULE ENGINE
# =====================================================

if __name__ == "__main__":

    print("\nFRAUDGUARD - TRANSACTION MONITORING SYSTEM")
    print("=" * 50)

    # Load transaction data
    transactions = pd.read_csv("data/transactions.csv")

    print("Loading transactions:", len(transactions))

    # Execute fraud rules
    results = evaluate_transactions(transactions)

    # Save analyzed transactions
    results.to_csv(
        "data/analyzed_transactions.csv",
        index=False
    )

    # =================================================
    # 7. DISPLAY RESULTS
    # =================================================

    print("\nRULE ENGINE EXECUTION SUCCESSFUL")
    print("=" * 50)

    print("Total transactions:", len(results))

    print(
        "Flagged transactions:",
        int(results["alert_status"].sum())
    )

    print(
        "Unflagged transactions:",
        int((~results["alert_status"]).sum())
    )

    print("\nRISK DISTRIBUTION")
    print("-" * 30)

    print(results["risk_level"].value_counts())

    print("\nRULE-WISE TRIGGER COUNTS")
    print("-" * 30)

    for rule_id, details in RULES.items():

        print(
            f"{rule_id} - {details['name']}: "
            f"{int(results[rule_id].sum())}"
        )

    print("\nSAMPLE SUSPICIOUS TRANSACTIONS")
    print("-" * 50)

    suspicious = results[results["alert_status"]]

    print(
        suspicious[
            [
                "transaction_id",
                "customer_id",
                "amount",
                "risk_score",
                "risk_level",
                "triggered_rules"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nAnalyzed dataset saved successfully!")
    print("Location: data/analyzed_transactions.csv")
