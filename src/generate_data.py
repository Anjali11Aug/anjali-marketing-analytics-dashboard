import pandas as pd
import numpy as np
import os

np.random.seed(42)

def generate():

    os.makedirs("data", exist_ok=True)

    n = 1800

    platforms = ["Google", "Meta", "Amazon"]
    campaigns = ["A", "B"]

    dates = pd.date_range("2025-01-01", periods=n)

    df = pd.DataFrame({
        "date": dates,
        "platform": np.random.choice(platforms, n),
        "campaign": np.random.choice(campaigns, n),
        "impressions": np.random.randint(2000, 20000, n),
        "clicks": np.random.randint(100, 3000, n),
        "cost": np.random.uniform(200, 2500, n),
        "conversions": np.random.randint(20, 400, n)
    })

    df.to_csv("data/raw_campaign.csv", index=False)


if __name__ == "__main__":
    generate()
