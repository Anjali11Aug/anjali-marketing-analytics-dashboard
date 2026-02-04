import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from sklearn.linear_model import LinearRegression
from src.metrics import overall_metrics, campaign_summary


import os
from src.pipeline import run_pipeline

# auto create data if not present
if not os.path.exists("data/clean_campaign.csv"):
    os.makedirs("data", exist_ok=True)
    run_pipeline()

st.set_page_config(layout="wide")

st.title("Campaign Optimization & Analytics Dashboard")

# always load from project root
df = pd.read_csv("data/clean_campaign.csv")

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("Filters")

platforms = st.sidebar.multiselect(
    "Platform",
    df["platform"].unique(),
    default=df["platform"].unique()
)

campaigns = st.sidebar.multiselect(
    "Campaign",
    df["campaign"].unique(),
    default=df["campaign"].unique()
)

filtered = df[
    (df["platform"].isin(platforms)) &
    (df["campaign"].isin(campaigns))
]

# =============================
# Current Budget (baseline)
# =============================
st.subheader("📊 Current Spend Overview")

total_budget = filtered["cost"].sum()
total_roi = filtered["ROI"].sum()

c1, c2 = st.columns(2)
c1.metric("Current Total Budget ($)", round(total_budget, 2))
c2.metric("Current ROI ($)", round(total_roi, 2))


# -------------------------
# KPI metrics
# -------------------------
st.subheader("Key Metrics")

metrics = overall_metrics(filtered)

cols = st.columns(len(metrics))
for i, (k, v) in enumerate(metrics.items()):
    cols[i].metric(k, v)

# -------------------------
# ROI trend
# -------------------------
st.subheader("ROI Trend")

fig, ax = plt.subplots()
filtered.groupby("date")["ROI"].sum().plot(ax=ax)
st.pyplot(fig)

# -------------------------
# Platform ranking
# -------------------------
st.subheader("Platform Ranking")

platform_roi = (
    filtered.groupby("platform")["ROI"]
    .mean()
    .sort_values(ascending=False)
)

st.dataframe(platform_roi)

best_platform = platform_roi.index[0]

# -------------------------
# Budget recommendation
# -------------------------
# =============================
# Budget Recommendation
# =============================

st.subheader("Budget Reallocation Recommendation")

summary = (
    filtered.groupby("platform")
    .agg({
        "ROI": "mean",
        "cost": "mean"
    })
)

summary["ROI_per_dollar"] = summary["ROI"] / summary["cost"]

st.dataframe(summary)

if summary.empty:
    st.warning("No data available.")

elif len(summary) == 1:
    only = summary.index[0]
    st.info(f"Only {only} selected — no comparison possible.")

else:
    best = summary["ROI_per_dollar"].idxmax()
    worst = summary["ROI_per_dollar"].idxmin()

    shift_pct = st.slider("Budget shift (%)", 0, 100, 30) / 100

    diff = (
        summary.loc[best, "ROI_per_dollar"] -
        summary.loc[worst, "ROI_per_dollar"]
    )

    gain = diff * total_budget * shift_pct

    new_roi = total_roi + gain

    st.success(
        f"""Shift {int(shift_pct*100)}% budget from {worst} → {best}

Current ROI: ${round(total_roi,2)}
New ROI: ${round(new_roi,2)}
Estimated Gain: ${round(gain,2)}
"""
    )




# -------------------------
# What-if simulator
# -------------------------
st.subheader("Budget Scaling & ROI Forecast")



budget = st.slider("Budget ($)", 1000, 20000, 5000)

avg_cpa = filtered["CPA"].mean()
conv = budget / avg_cpa
revenue = conv * 50
roi = revenue - budget

c1, c2, c3 = st.columns(3)
c1.metric("Conversions", int(conv))
c2.metric("Revenue ($)", round(revenue, 2))
c3.metric("ROI ($)", round(roi, 2))

# -------------------------
# A/B testing
# -------------------------
st.subheader("A/B Testing")

a = filtered[filtered["campaign"] == "A"]["ROI"]
b = filtered[filtered["campaign"] == "B"]["ROI"]

if len(a) > 0 and len(b) > 0:
    _, p = ttest_ind(a, b)
    st.write("p-value:", round(p, 4))

# -------------------------
# Forecasting
# -------------------------
st.subheader("ROI Forecast")

daily = filtered.groupby("date")["ROI"].sum().reset_index()

daily["t"] = np.arange(len(daily))

model = LinearRegression().fit(daily[["t"]], daily["ROI"])

future = pd.DataFrame({
    "t": np.arange(len(daily), len(daily) + 30)
})

pred = model.predict(future)


fig2, ax2 = plt.subplots()
ax2.plot(daily["ROI"])
ax2.plot(range(len(daily), len(daily)+30), pred)
st.pyplot(fig2)
