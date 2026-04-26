import yfinance as yf


def test_yfinance():
    tickers = ["NVDA", "CRDO", "BESIY", "COHR"]
    print(f"Testing yfinance for: {tickers}")
    try:
        # Try a simple download
        data = yf.download(tickers, period="1d", group_by="ticker")
        if data.empty:
            print("Download returned empty data.")
        else:
            print("Successfully downloaded data:")
            for t in tickers:
                if t in data and not data[t].empty:
                    print(f"  - {t}: {data[t]['Close'].iloc[-1]}")
                else:
                    print(f"  - {t}: FAILED")

        # Try ticker info (often fails when download works)
        print("\nTesting info retrieval:")
        for t in tickers:
            ticker_obj = yf.Ticker(t)
            try:
                # Use .fast_info instead of .info if .info fails
                info = ticker_obj.fast_info
                print(f"  - {t} Fast Info Price: {info['lastPrice']}")
            except Exception as e:
                print(f"  - {t} Fast Info failed: {e}")

    except Exception as e:
        print(f"Global yfinance failure: {e}")


if __name__ == "__main__":
    test_yfinance()
