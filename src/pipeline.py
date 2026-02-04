import pandas as pd
import os
from src.generate_data import generate

RAW = "data/raw_campaign.csv"
CLEAN = "data/clean_campaign.csv"


def extract():
    if not os.path.exists(RAW):
        print("Generating raw data...")
        generate()

    return pd.read_csv(RAW)


def transform(df):
    df["CTR"] = df["clicks"] / df["impressions"]
    df["CPC"] = df["cost"] / df["clicks"]
    df["CPA"] = df["cost"] / df["conversions"]
    df["revenue"] = df["conversions"] * 50
    df["ROI"] = df["revenue"] - df["cost"]
    return df


def load(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv(CLEAN, index=False)


def run_pipeline():
    df = extract()
    df = transform(df)
    load(df)
