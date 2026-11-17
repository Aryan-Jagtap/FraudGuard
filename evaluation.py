
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# Load analyzed transactions
df = pd.read_csv("data/analyzed_transactions.csv")

# Actual labels from the synthetic dataset
y_actual = df["is_fraud"].astype(int)

# Prediction: 1 if at least one detection rule generated an alert
y_predicted = df["alert_status"].astype(int)

# Calculate performance metrics
accuracy = accuracy_score(y_actual, y_predicted)
precision = precision_score(y_actual, y_predicted, zero_division=0)
recall = recall_score(y_actual, y_predicted, zero_division=0)
f1 = f1_score(y_actual, y_predicted, zero_division=0)

print("\n========== FRAUD DETECTION PERFORMANCE ==========")

print(f"Total Transactions : {len(df)}")
print(f"Actual Fraud Cases : {y_actual.sum()}")
print(f"Generated Alerts   : {y_predicted.sum()}")

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")

# Confusion matrix
tn, fp, fn, tp = confusion_matrix(
    y_actual,
    y_predicted,
    labels=[0, 1]
).ravel()

print("\n========== CONFUSION MATRIX ==========")
print(f"True Positives  (TP): {tp}")
print(f"True Negatives  (TN): {tn}")
print(f"False Positives (FP): {fp}")
print(f"False Negatives (FN): {fn}")

print("\n========== CLASSIFICATION REPORT ==========")
print(classification_report(
    y_actual,
    y_predicted,
    target_names=["Legitimate", "Fraud"],
    zero_division=0
))

# Save results
results = pd.DataFrame([{
    "total_transactions": len(df),
    "actual_fraud": int(y_actual.sum()),
    "generated_alerts": int(y_predicted.sum()),
    "accuracy": accuracy,
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "true_positives": int(tp),
    "true_negatives": int(tn),
    "false_positives": int(fp),
    "false_negatives": int(fn)
}])

results.to_csv("reports/performance_report.csv", index=False)

print("Performance report saved to reports/performance_report.csv")
