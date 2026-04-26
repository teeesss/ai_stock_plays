import os

import pandas as pd


def audit_tradability():
    csv_path = "cpo_master_ultimate.csv"
    if not os.path.exists(csv_path):
        print("CSV not found.")
        return

    df = pd.read_csv(csv_path)

    # Add Status column if not exists
    if "Status" not in df.columns:
        df.insert(3, "Status", "Public")

    # Private Companies
    private_tickers = [
        "CelestialAI",
        "AYAR",
        "RANV",
        "SCINTIL",
        "ALMU",
        "Celestial AI",
        "Ayar Labs",
        "Scintil Photonics",
        "Ranovus",
    ]

    # ETFs
    etf_tickers = ["XSD", "LADR", "PTF", "SMH", "SOXX"]

    def get_status(row):
        ticker = str(row["Ticker"])
        bucket = str(row["Bucket"]).lower()

        if ticker in private_tickers or any(p in str(row["Company"]) for p in private_tickers):
            return "Private"
        if ticker in etf_tickers or "etf" in bucket:
            return "ETF"
        return "Public"

    df["Status"] = df.apply(get_status, axis=1)

    # Perform a few specific cleanups
    df.loc[df["Ticker"] == "CelestialAI", "Status"] = "Private"
    df.loc[df["Ticker"] == "AYAR", "Status"] = "Private"
    df.loc[df["Ticker"] == "ALMU", "Status"] = "Private"

    df.to_csv(csv_path, index=False)
    print(f"Audited {len(df)} plays. Status column updated.")

    # Stats
    print(f"Public: {len(df[df['Status'] == 'Public'])}")
    print(f"Private: {len(df[df['Status'] == 'Private'])}")
    print(f"ETF: {len(df[df['Status'] == 'ETF'])}")


if __name__ == "__main__":
    audit_tradability()
