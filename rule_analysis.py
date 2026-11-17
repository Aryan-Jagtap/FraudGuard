
import pandas as pd

df = pd.read_csv("data/analyzed_transactions.csv")

rules = {
    "R001": "High Value",
    "R002": "High Velocity",
    "R003": "Failed Attempts",
    "R004": "Unusual Location",
    "R005": "Unusual Spending"
}

results = []

for rule, description in rules.items():

    triggered = df[df[rule] == 1]

    true_positives = int(triggered["is_fraud"].sum())
    false_positives = len(triggered) - true_positives

    precision = (
        true_positives / len(triggered)
        if len(triggered) > 0 else 0
    )

    results.append({
        "Rule": rule,
        "Description": description,
        "Total Alerts": len(triggered),
        "Actual Fraud": true_positives,
        "False Positives": false_positives,
        "Precision": round(precision, 4)
    })

report = pd.DataFrame(results)

print("\n========== RULE-WISE PERFORMANCE ==========")
print(report.to_string(index=False))

report.to_csv("reports/rule_analysis.csv", index=False)

print("\nSaved: reports/rule_analysis.csv")
