
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set up Streamlit page
st.set_page_config(page_title="QA Cost Simulator", layout="wide")
st.title("Housekeeping QA Cost Simulator")

# --- Sidebar Inputs ---
st.sidebar.header("Simulation Inputs")

TotalRooms = st.sidebar.number_input("Total Rooms per Month", value=6200)
ErrorRate = st.sidebar.slider("Error Rate (before QA)", 0.0, 0.3, 0.10, 0.01)
QAEffectiveness = st.sidebar.slider("QA Effectiveness", 0.0, 1.0, 0.90, 0.01)
GuestDetectionRate = st.sidebar.slider("Guest Detection Rate", 0.0, 0.2, 0.05, 0.01)

BaseQA_CostPerRoom = st.sidebar.number_input("Base QA Cost per Room", value=8.0)
Beta_QA_CostShape = st.sidebar.slider("QA Cost Inefficiency Factor", 0.0, 5.0, 0.0, 0.1)

BaseGuestIssueCost = st.sidebar.number_input("Base Guest Issue Cost", value=100.0)
Alpha_GuestIssueNonlinearity = st.sidebar.slider("Guest Issue Nonlinearity", 0.0, 2.0, 0.8, 0.1)

n_simulations = st.sidebar.slider("Simulations per QA Rate", 100, 2000, 1000, 100)

# --- Simulation ---
st.subheader("Simulation Results")
qa_rates = np.linspace(0, 1, 21)
simulation_results = []

for rate in qa_rates:
    for _ in range(n_simulations):
        sampled_error_rate = np.clip(np.random.normal(ErrorRate, 0.02), 0, 1)
        sampled_qa_effectiveness = np.random.triangular(0.85, QAEffectiveness, 0.95)
        sampled_guest_detection = np.random.uniform(max(0.0, GuestDetectionRate - 0.01), min(1.0, GuestDetectionRate + 0.01))
        guest_issue_cost = np.random.choice([50, 200], p=[0.7, 0.3])

        RoomsChecked = TotalRooms * rate
        EstimatedErrors = TotalRooms * sampled_error_rate

        ErrorsInChecked = EstimatedErrors * rate
        ErrorsDetected = ErrorsInChecked * sampled_qa_effectiveness
        ErrorsMissed = ErrorsInChecked * (1 - sampled_qa_effectiveness)
        ErrorsInUnchecked = EstimatedErrors * (1 - rate)

        GuestFacingIssues = (ErrorsMissed + ErrorsInUnchecked) * sampled_guest_detection

        if rate == 0:
            QA_Cost = 0
        else:
            QA_CostPerRoom = BaseQA_CostPerRoom * (1 + Beta_QA_CostShape * (1 - rate))
            QA_Cost = RoomsChecked * QA_CostPerRoom

        GuestIssueCostTotal = guest_issue_cost * GuestFacingIssues * (1 + Alpha_GuestIssueNonlinearity * GuestFacingIssues)
        TotalCost = QA_Cost + GuestIssueCostTotal

        simulation_results.append({
            "QA Rate": rate,
            "Total Cost": TotalCost,
            "QA Cost": QA_Cost,
            "Guest Issue Cost": GuestIssueCostTotal
        })

# --- DataFrame and Summary ---
df_sim = pd.DataFrame(simulation_results)
summary_df = df_sim.groupby("QA Rate")["Total Cost"].agg(
    MeanTotalCost="mean",
    P95=lambda x: np.percentile(x, 95)
).reset_index()

# --- Plotting ---
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(summary_df["QA Rate"], summary_df["MeanTotalCost"], label="Mean Total Cost", linewidth=2)
ax.plot(summary_df["QA Rate"], summary_df["P95"], label="95th Percentile (Risk)", linestyle="--")
ax.set_xlabel("QA Check Rate")
ax.set_ylabel("Total Cost (£)")
ax.set_title("Total Cost vs QA Check Rate")
ax.legend()
ax.grid(True)

st.pyplot(fig)

st.markdown("""
**How to Use This Tool:**
- Adjust the sliders and inputs on the left to reflect your assumptions or scenarios.
- The chart shows both the expected cost (mean) and the risk (95th percentile).
- Use it to identify the QA check rate that best balances cost and guest satisfaction risk.
""")
