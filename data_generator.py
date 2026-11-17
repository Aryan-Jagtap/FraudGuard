
import pandas as pd
import numpy as np
from pathlib import Path


def generate_transactions(n=5000, seed=42):

    rng = np.random.default_rng(seed)

    # Sample Indian cities
    locations = [
        "Mumbai", "Pune", "Delhi", "Bangalore",
        "Hyderabad", "Chennai", "Kolkata", "Jaipur"
    ]

    merchant_categories = [
        "Shopping", "Groceries", "Travel",
        "Food", "Electronics", "Healthcare", "Entertainment"
    ]

    # Create customer profiles
    customers = [f"CUST{i:04d}" for i in range(1, 501)]

    customer_home = {
        customer: rng.choice(locations)
        for customer in customers
    }

    customer_avg_spending = {
        customer: rng.uniform(500, 12000)
        for customer in customers
    }

    # Generate basic transaction records
    customer_ids = rng.choice(customers, n)

    amounts = [
        rng.lognormal(
            mean=np.log(customer_avg_spending[c]),
            sigma=0.65
        )
        for c in customer_ids
    ]

    timestamps = (
        pd.Timestamp("2026-10-01")
        + pd.to_timedelta(
            rng.integers(0, 30 * 24 * 60, n), unit="m"
        )
    )

    home_locations = [
        customer_home[c] for c in customer_ids
    ]

    transaction_locations = [
        home if rng.random() < 0.90
        else rng.choice([loc for loc in locations if loc != home])
        for home in home_locations
    ]

    df = pd.DataFrame({
        "transaction_id": [f"TXN{i:06d}" for i in range(1, n + 1)],
        "customer_id": customer_ids,
        "amount": np.round(amounts, 2),
        "timestamp": timestamps,
        "merchant_category": rng.choice(merchant_categories, n),
        "location": transaction_locations,
        "home_location": home_locations,
        "device_id": [
            f"DEV{rng.integers(1, 1001):04d}" for _ in range(n)
        ],
        "failed_attempts": rng.choice(
            [0, 1, 2], n, p=[0.85, 0.10, 0.05]
        ),
        "transaction_status": rng.choice(
            ["SUCCESS", "FAILED"], n, p=[0.95, 0.05]
        ),
        "is_fraud": 0
    })

    # Select different transactions for simulated fraud patterns
    indices = rng.permutation(n)

    # Pattern 1: Unusually high transaction amounts
    high_amount_idx = indices[:100]
    df.loc[high_amount_idx, "amount"] = np.round(
        rng.uniform(60000, 150000, len(high_amount_idx)), 2
    )
    df.loc[high_amount_idx, "is_fraud"] = 1

    # Pattern 2: Multiple transactions within one minute
    velocity_idx = indices[100:180]

    for i in range(0, len(velocity_idx), 4):
        group = velocity_idx[i:i + 4]
        if len(group) == 4:
            customer = df.loc[group[0], "customer_id"]
            df.loc[group, "customer_id"] = customer

            base_time = df.loc[group[0], "timestamp"]
            df.loc[group, "timestamp"] = [
                base_time + pd.Timedelta(seconds=j * 10)
                for j in range(4)
            ]

            df.loc[group, "is_fraud"] = 1

    # Pattern 3: Multiple failed attempts
    failed_idx = indices[180:240]
    df.loc[failed_idx, "failed_attempts"] = 3
    df.loc[failed_idx, "transaction_status"] = "FAILED"
    df.loc[failed_idx, "is_fraud"] = 1

    # Pattern 4: Transaction from unusual location
    location_idx = indices[240:300]

    for idx in location_idx:
        home = df.loc[idx, "home_location"]
        other_locations = [loc for loc in locations if loc != home]
        df.loc[idx, "location"] = rng.choice(other_locations)

    df.loc[location_idx, "is_fraud"] = 1

    # Sort transactions chronologically
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


if __name__ == "__main__":

    df = generate_transactions()

    output_path = Path("data/transactions.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    print("Transaction dataset generated successfully!")
    print("---------------------------------------------")
    print("Total transactions:", len(df))
    print("Fraudulent transactions:", df["is_fraud"].sum())
    print("Legitimate transactions:", (df["is_fraud"] == 0).sum())
    print("Fraud percentage:", round(df["is_fraud"].mean() * 100, 2), "%")
    print("Dataset saved at:", output_path)
