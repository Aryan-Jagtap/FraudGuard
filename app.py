
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="FraudGuard | Banking Risk Monitor",
    page_icon="🛡️",
    layout="wide"
)

# -----------------------------------
# LOAD DATA
# -----------------------------------

@st.cache_data
def load_data():
    connection = sqlite3.connect("database/fraudguard.db")

    df = pd.read_sql_query(
        "SELECT * FROM transactions",
        connection
    )

    connection.close()

    return df


try:
    df = load_data()
except Exception:
    st.error("Database not found. Run: python database.py")
    st.stop()

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("🛡️ FraudGuard")

st.sidebar.caption("Banking Transaction Monitoring System")

st.sidebar.divider()

risk_options = ["All"] + sorted(df["risk_level"].dropna().unique().tolist())

selected_risk = st.sidebar.selectbox(
    "Filter by Risk Level",
    risk_options
)

customers = ["All"] + sorted(df["customer_id"].dropna().unique().tolist())

selected_customer = st.sidebar.selectbox(
    "Filter by Customer",
    customers
)

# -----------------------------------
# FILTER DATA
# -----------------------------------

filtered_df = df.copy()

if selected_risk != "All":
    filtered_df = filtered_df[
        filtered_df["risk_level"] == selected_risk
    ]

if selected_customer != "All":
    filtered_df = filtered_df[
        filtered_df["customer_id"] == selected_customer
    ]

alerts = filtered_df[filtered_df["alert_status"] == 1]

# -----------------------------------
# DASHBOARD HEADER
# -----------------------------------

st.title("🛡️ FraudGuard")
st.subheader("Banking Transaction Monitoring & Risk Analytics")

st.caption(
    "Synthetic transaction dataset | Rule-based fraud detection prototype"
)

st.divider()

# -----------------------------------
# KPI CARDS
# -----------------------------------

total_transactions = len(filtered_df)
total_alerts = len(alerts)

high_risk = len(
    filtered_df[filtered_df["risk_level"] == "High"]
)

medium_risk = len(
    filtered_df[filtered_df["risk_level"] == "Medium"]
)

low_risk = len(
    filtered_df[filtered_df["risk_level"] == "Low"]
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Transactions", f"{total_transactions:,}")
col2.metric("Flagged Alerts", f"{total_alerts:,}")
col3.metric("High Risk", f"{high_risk:,}")
col4.metric("Medium Risk", f"{medium_risk:,}")
col5.metric("Low Risk", f"{low_risk:,}")

st.divider()

# -----------------------------------
# RISK DISTRIBUTION
# -----------------------------------

st.subheader("Risk Distribution")

col1, col2 = st.columns(2)

risk_counts = (
    filtered_df["risk_level"]
    .value_counts()
    .reindex(["Legitimate", "Low", "Medium", "High"], fill_value=0)
    .reset_index()
)

risk_counts.columns = ["Risk Level", "Count"]

with col1:
    fig = px.pie(
        risk_counts,
        names="Risk Level",
        values="Count",
        hole=0.45,
        title="Transaction Risk Breakdown"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# RULE PERFORMANCE
# -----------------------------------

rule_columns = ["R001", "R002", "R003", "R004", "R005"]

rule_labels = {
    "R001": "High Value",
    "R002": "High Velocity",
    "R003": "Failed Attempts",
    "R004": "Unusual Location",
    "R005": "Unusual Spending"
}

rule_counts = pd.DataFrame({
    "Rule": [rule_labels[r] for r in rule_columns],
    "Alerts": [int(filtered_df[r].sum()) for r in rule_columns]
})

with col2:
    fig = px.bar(
        rule_counts,
        x="Rule",
        y="Alerts",
        title="Rule-wise Alert Generation",
        text="Alerts"
    )

    fig.update_layout(xaxis_title="Detection Rule",
                      yaxis_title="Number of Triggered Transactions")

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------------
# TRANSACTION INVESTIGATION
# -----------------------------------

st.subheader("🚨 Suspicious Transaction Investigation")

if len(alerts) > 0:

    display_columns = [
        "transaction_id",
        "customer_id",
        "amount",
        "timestamp",
        "location",
        "risk_score",
        "risk_level",
        "triggered_rules"
    ]

    st.dataframe(
        alerts[display_columns].sort_values(
            "risk_score",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No flagged transactions match the selected filters.")

st.divider()

# -----------------------------------
# UAT REPORT
# -----------------------------------

st.subheader("🧪 Rule Validation – UAT Results")

try:
    uat = pd.read_csv("reports/uat_report.csv")

    passed = (uat["status"] == "PASS").sum()
    failed = (uat["status"] == "FAIL").sum()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Test Cases", len(uat))
    c2.metric("Passed", int(passed))
    c3.metric("Failed", int(failed))

    st.dataframe(uat, use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.warning("UAT report not found. Run python test_uat.py")

# -----------------------------------
# FOOTER
# -----------------------------------

st.divider()

st.caption(
    "FraudGuard | Academic prototype using synthetic data. "
    "Alerts indicate rule matches, not confirmed fraud."
)
