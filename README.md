# FraudGuard – Banking Transaction Monitoring & Rule-Based Fraud Detection

\<p align="center">   \<strong>A rule-based banking transaction monitoring system with fraud alerts, risk scoring, analytics, UAT testing and a simulated release workflow.\</strong> \</p>

\<p align="center">   \<a href="[https://fraudguard-aryan-jagtap.streamlit.app/](https://fraudguard-aryan-jagtap.streamlit.app/)">Live Demo\</a> ·   \<a href="[https://github.com/Aryan-Jagtap/FraudGuard](https://github.com/Aryan-Jagtap/FraudGuard)">GitHub Repository\</a> \</p>

---

## Live Demo

**Try FraudGuard here:** [https://fraudguard-aryan-jagtap.streamlit.app/](https://fraudguard-aryan-jagtap.streamlit.app/)

FraudGuard is an academic prototype that demonstrates how banking transactions can be monitored using configurable fraud detection rules. It assigns risk scores, identifies suspicious transactions and presents monitoring results through an interactive dashboard.

> **Disclaimer:** This project uses synthetic transaction data. It is not connected to any real bank, payment gateway or production banking system.

## Dashboard Preview

### 1. Dashboard Overview



### 2. Fraud Alerts and Transaction Monitoring



### 3. User Acceptance Testing Results



---

## Key Features

- **Transaction Monitoring:** Processes and analyzes 5,000 synthetic banking transactions.
- **Rule-Based Fraud Detection:** Implements five configurable rules to identify suspicious transaction patterns.
- **Risk Scoring:** Assigns risk scores and categorizes transactions into Legitimate, Low, Medium and High risk levels.
- **Fraud Alert Generation:** Identifies transactions that trigger one or more detection rules.
- **Interactive Dashboard:** Displays transaction KPIs, risk distribution, rule-wise alerts and suspicious transactions.
- **SQL-Based Analysis:** Uses SQLite to store transaction records and execute analytical queries.
- **UAT Testing:** Includes six test cases to verify fraud detection rule behavior.
- **Performance Evaluation:** Measures accuracy, precision, recall and F1-score.
- **Rule Tuning:** Analyzes false positives and adjusts detection conditions to improve alert quality.
- **Release Simulation:** Demonstrates testing, release packaging, database validation and post-release verification (PVT).

## Technology Stack

| Technology              | Purpose                                    |
| ----------------------- | ------------------------------------------ |
| Python                  | Core development and fraud detection logic |
| Pandas & NumPy          | Data generation and processing             |
| Streamlit               | Interactive monitoring dashboard           |
| Plotly                  | Data visualization                         |
| SQLite                  | Transaction database                       |
| SQL                     | Transaction analysis and reporting         |
| Scikit-learn            | Model evaluation metrics                   |
| Pytest / Python testing | Testing support                            |

## Fraud Detection Rules

FraudGuard uses five configurable rules. Each rule contributes to the transaction's cumulative risk score.

| Rule ID | Detection Condition                                                                             | Risk Score |
| ------- | ----------------------------------------------------------------------------------------------- | ---------: |
| R001    | Transaction amount exceeds ₹50,000                                                              |         30 |
| R002    | More than 3 transactions occur within a rolling 60-second window                                |         40 |
| R003    | Failed transaction attempts are 3 or more                                                       |         35 |
| R004    | Transaction location differs from home location AND amount exceeds ₹20,000                      |         25 |
| R005    | Transaction amount exceeds 3 times the customer's median transaction amount AND exceeds ₹20,000 |         30 |

### Risk Classification

| Risk Score | Risk Level |
| ---------- | ---------- |
| 0          | Legitimate |
| 1–29       | Low        |
| 30–59      | Medium     |
| 60–100     | High       |

The cumulative risk score is capped at 100. A transaction triggering at least one rule is marked as an alert.

## Project Architecture

```text
                 Synthetic Transaction Data
                           |
                           v
                    Data Generator
                           |
                           v
                    Rule Engine
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
          R001-R005    Risk Scoring   Alert Generation
             |             |             |
             +-------------+-------------+
                           |
                           v
                  Analyzed Transactions
                           |
                +----------+----------+
                |                     |
                v                     v
          SQLite Database       Performance Evaluation
                |
                v
          SQL Analysis
                |
                v
        Streamlit Dashboard
                |
                v
         Fraud Monitoring

       UAT Testing and Release Simulation
```

## Dataset

The project generates a synthetic dataset with:

- 5,000 banking transactions
- 500 unique customers
- 30 days of transaction activity
- 300 injected fraud-labelled transactions
- 6% synthetic fraud prevalence

Transaction attributes include transaction amount, timestamp, customer ID, merchant category, location, home location, device ID, failed attempts and transaction status.

The `is_fraud` label is used only for retrospective performance evaluation. It is not used by the rule engine to generate predictions.

## Performance Evaluation

The tuned rule engine was evaluated against the synthetic fraud labels.

| Metric                    | Result |
| ------------------------- | -----: |
| Total Transactions        |  5,000 |
| Actual Fraud Transactions |    300 |
| Generated Alerts          |    314 |
| Accuracy                  | 95.28% |
| Precision                 | 60.19% |
| Recall                    | 63.00% |
| F1-Score                  | 61.56% |

### Confusion Matrix

|                   | Predicted Fraud | Predicted Legitimate |
| ----------------- | --------------: | -------------------: |
| Actual Fraud      |        189 (TP) |             111 (FN) |
| Actual Legitimate |        125 (FP) |           4,575 (TN) |

### Rule Tuning

Rule tuning was performed to reduce false-positive alerts.

- The location-based rule was refined to consider transaction amount alongside location mismatch.
- The unusual-spending rule was refined using customer-relative spending thresholds.
- False positives reduced from 657 to 125 in the exploratory comparison.

**Important evaluation limitation:** These are exploratory results on the same synthetic dataset used during rule tuning, not independent validation results. A separate holdout dataset and time-based validation would be needed for a fair assessment. The customer median baseline in R005 is also calculated across the full dataset in this prototype; a production implementation should calculate it using only transactions available before the transaction being evaluated.

## User Acceptance Testing (UAT)

Six test cases were implemented to verify expected rule behavior.

| Test Case | Scenario                         | Expected Result |
| --------- | -------------------------------- | --------------- |
| TC001     | Normal transaction               | No alert        |
| TC002     | High-value transaction           | R001            |
| TC003     | High transaction velocity        | R002            |
| TC004     | Multiple failed attempts         | R003            |
| TC005     | Unusual location and high amount | R004            |
| TC006     | Unusual customer spending        | R005            |

**UAT Result: 6 Passed, 0 Failed.**

## Release and Production Verification Simulation

A local release workflow was implemented to demonstrate a simplified banking-system release process.

The workflow includes:

1. Testing and UAT validation.
2. Release package creation.
3. Database record validation.
4. Release package integrity checks.
5. Release manifest verification.
6. Post-Verification Testing (PVT).

**Result: 6 release checks passed, 0 failed.**

This is a local release simulation and does not represent an actual production deployment or integration with a banking system.

## Project Structure

```text
FraudGuard/
│
├── app.py
├── data_generator.py
├── rule_engine.py
├── test_uat.py
├── database.py
├── sql_analysis.py
├── evaluation.py
├── rule_analysis.py
├── rule_tuning_analysis.py
├── release_workflow.py
│
├── data/
│   ├── transactions.csv
│   └── analyzed_transactions.csv
│
├── database/
│   └── fraudguard.db
│
├── reports/
│   ├── uat_report.csv
│   ├── performance_report.csv
│   ├── rule_analysis.csv
│   └── pvt_report.csv
│
├── screenshots/
│   ├── dashboard_overview.png
│   ├── fraud_alerts.png
│   └── uat_results.png
│
├── requirements.txt
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Aryan-Jagtap/FraudGuard.git
cd FraudGuard
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate synthetic transactions

```bash
python data_generator.py
```

### 5. Run the fraud detection engine

```bash
python rule_engine.py
```

### 6. Run UAT test cases

```bash
python test_uat.py
```

### 7. Store transactions in SQLite

```bash
python database.py
```

### 8. Generate evaluation reports

```bash
python evaluation.py
python rule_analysis.py
```

### 9. Run the release simulation

```bash
python release_workflow.py
```

### 10. Launch the dashboard

```bash
streamlit run app.py
```

## Future Improvements

- Introduce machine learning models for anomaly detection.
- Implement time-based validation and more realistic fraud patterns.
- Add configurable rules through the dashboard.
- Implement real-time transaction stream processing.
- Improve customer-specific behavioral baselines.
- Add role-based access control and audit logging.
- Explore integration with secure banking APIs in a controlled environment.

## Author

**Aryan Jagtap**

Computer Engineering Student

- GitHub: [https://github.com/Aryan-Jagtap](https://github.com/Aryan-Jagtap)
- Project Repository: [https://github.com/Aryan-Jagtap/FraudGuard](https://github.com/Aryan-Jagtap/FraudGuard)
- Live Demo: [https://fraudguard-aryan-jagtap.streamlit.app/](https://fraudguard-aryan-jagtap.streamlit.app/)

---

*FraudGuard is an academic portfolio project developed to demonstrate transaction monitoring, rule-based fraud detection, risk analysis, UAT and release verification concepts.*
