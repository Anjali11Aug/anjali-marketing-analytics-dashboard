def overall_metrics(df):
    return {
        "Impressions": int(df["impressions"].sum()),
        "Clicks": int(df["clicks"].sum()),
        "Conversions": int(df["conversions"].sum()),
        "Spend ($)": round(df["cost"].sum(), 2),
        "Revenue ($)": round(df["revenue"].sum(), 2),
        "ROI ($)": round(df["ROI"].sum(), 2)
    }


def campaign_summary(df):
    return (
        df.groupby("campaign")[["CTR", "CPC", "CPA", "ROI"]]
        .mean()
        .reset_index()
    )
