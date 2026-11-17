
import pandas as pd

df = pd.read_csv("data/analyzed_transactions.csv")

# Retrospective analysis only:
# is_fraud is used to evaluate rules, never to make predictions.

print("\n========== R004: LOCATION ANALYSIS ==========")

location_alerts = df[df["R004"] == 1].copy()

location_alerts["failed_attempt_flag"] = (
    location_alerts["failed_attempts"] >= 1
)

location_alerts["high_amount_flag"] = (
    location_alerts["amount"] > 20000
)

print("\nLocation alerts by actual fraud label:")
print(
    location_alerts.groupby("is_fraud").agg(
        transactions=("transaction_id", "count"),
        average_amount=("amount", "mean"),
        failed_attempts=("failed_attempt_flag", "sum"),
        high_amount=("high_amount_flag", "sum")
    )
)

print("\nPotential R004 refinement combinations:")

conditions = {
    "Location mismatch only": pd.Series(True, index=location_alerts.index),
    "Location + amount > 20000": location_alerts["high_amount_flag"],
    "Location + failed attempts": location_alerts["failed_attempt_flag"],
    "Location + amount OR failed attempts": (
        location_alerts["high_amount_flag"]
        | location_alerts["failed_attempt_flag"]
    ),
    "Location + amount AND failed attempts": (
        location_alerts["high_amount_flag"]
        & location_alerts["failed_attempt_flag"]
    )
}

for name, condition in conditions.items():

    subset = location_alerts[condition]

    total = len(subset)
    fraud = int(subset["is_fraud"].sum())

    precision = fraud / total if total else 0

    print(
        f"{name}: "
        f"Alerts={total}, "
        f"Fraud={fraud}, "
        f"Precision={precision:.2%}"
    )


print("\n========== R005: UNUSUAL SPENDING ANALYSIS ==========")

spending_alerts = df[df["R005"] == 1].copy()

print("\nR005 transactions by actual fraud label:")
print(
    spending_alerts.groupby("is_fraud")["amount"].agg(
        ["count", "mean", "median", "min", "max"]
    )
)

print("\nAmount distribution for R005:")
print(
    spending_alerts["amount"].describe(
        percentiles=[0.25, 0.50, 0.75, 0.90]
    )
)

print("\n========== COMPLETED ==========")
