
import pandas as pd
from rule_engine import evaluate_transactions


def create_transaction(
    txn_id,
    customer,
    amount,
    timestamp,
    location="Mumbai",
    home_location="Mumbai",
    failed_attempts=0
):
    return {
        "transaction_id": txn_id,
        "customer_id": customer,
        "amount": amount,
        "timestamp": timestamp,
        "merchant_category": "Retail",
        "location": location,
        "home_location": home_location,
        "device_id": "DEVICE_001",
        "failed_attempts": failed_attempts,
        "transaction_status": "SUCCESS"
    }


test_cases = [
    {
        "id": "TC001",
        "scenario": "Normal Transaction",
        "transactions": [
            create_transaction(
                "T001", "C001", 500, "2026-01-01 12:00:00"
            )
        ],
        "expected": set()
    },
    {
        "id": "TC002",
        "scenario": "High Value Transaction",
        "transactions": [
            create_transaction(
                "T002", "C002", 80000, "2026-01-01 12:00:00"
            )
        ],
        "expected": {"R001"}
    },
    {
        "id": "TC003",
        "scenario": "High Transaction Velocity",
        "transactions": [
            create_transaction(
                f"T00{i}", "C003", 1000,
                f"2026-01-01 12:00:{i * 10:02d}"
            )
            for i in range(1, 5)
        ],
        "expected": {"R002"}
    },
    {
        "id": "TC004",
        "scenario": "Multiple Failed Attempts",
        "transactions": [
            create_transaction(
                "T004", "C004", 1000,
                "2026-01-01 12:00:00",
                failed_attempts=3
            )
        ],
        "expected": {"R003"}
    },
    {
        "id": "TC005",
        "scenario": "Unusual Location with High Amount",
        "transactions": [
            create_transaction(
                "T005", "C005", 25000,
                "2026-01-01 12:00:00",
                location="Delhi",
                home_location="Mumbai"
            )
        ],
        "expected": {"R004"}
    },
    {
        "id": "TC006",
        "scenario": "Unusual Spending above Minimum Amount",
        "transactions": [
            create_transaction(
                f"T00{i}", "C006", amount,
                f"2026-01-01 12:{i * 10:02d}:00"
            )
            for i, amount in enumerate(
                [100, 100, 100, 25000], start=1
            )
        ],
        "expected": {"R005"}
    }
]


results = []

for test in test_cases:

    df = pd.DataFrame(test["transactions"])

    analyzed = evaluate_transactions(df)

    actual = set()

    for rules in analyzed["triggered_rules"]:
        if rules != "None":
            actual.update(rules.split(", "))

    passed = actual == test["expected"]

    results.append({
        "test_id": test["id"],
        "scenario": test["scenario"],
        "expected_rules": ", ".join(sorted(test["expected"])) or "None",
        "actual_rules": ", ".join(sorted(actual)) or "None",
        "status": "PASS" if passed else "FAIL"
    })


report = pd.DataFrame(results)

report.to_csv("reports/uat_report.csv", index=False)

print("\n========== FRAUDGUARD UAT REPORT ==========")
print(report.to_string(index=False))

print("\nPassed:", (report["status"] == "PASS").sum())
print("Failed:", (report["status"] == "FAIL").sum())
print("Total:", len(report))
