import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
import yfinance as yf

# ─────────────────────────────────────────────────────────────
# GIGACPO Institutional 13F Fetcher
# V1.0 — Alpha Institutional Layer
# ─────────────────────────────────────────────────────────────

# Paths
ROOT = Path(__file__).parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
DB_PATH = ROOT / "database" / "CPO_MASTER_DATA.json"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "inst_13f.log"), logging.StreamHandler()]
)
log = logging.getLogger("inst_13f")

# Conviction Holders (Top Tier Hedge Funds / Institutional Targets)
CONVICTION_TARGETS = [
    "Vanguard Group", "Blackrock Inc.", "Whale Rock Capital", 
    "Altimeter Capital", "Coatue Management", "State Street Corp",
    "FMR, LLC", "Morgan Stanley"
]

def clean_ticker(ticker: str) -> str:
    return ticker.split(' / ')[0].strip()

from yahooquery import Ticker as YQTicker

def fetch_inst_data(ticker_symbol: str):
    """Retrieve institutional holders using yahooquery (bypasses yfinance crumbs)."""
    log.info(f"Fetching 13F data for ${ticker_symbol}...")
    try:
        t = YQTicker(ticker_symbol)
        df = t.institution_ownership
        
        if df is None or (isinstance(df, dict) and not df) or (hasattr(df, 'empty') and df.empty):
            log.warning(f"No institutional data for ${ticker_symbol}")
            return None
            
        holders = []
        # yahooquery returns a DataFrame or a dict depending on ticker validity
        if isinstance(df, dict):
             # Check if it has an error entry
             if ticker_symbol in df and isinstance(df[ticker_symbol], str):
                 log.error(f"Ticker ${ticker_symbol} error: {df[ticker_symbol]}")
                 return None
             return None

        for _, row in df.iterrows():
            holder_name = str(row.get('organization', 'Unknown'))
            holders.append({
                "holder": holder_name,
                "shares": int(row.get('position', 0)),
                "date_reported": str(row.get('reportDate', 'Unknown')),
                "pct_out": float(row.get('pctHeld', 0)) * 100, # Normalize to %
                "value": int(row.get('value', 0)),
                "is_conviction": any(target.lower() in holder_name.lower() for target in CONVICTION_TARGETS)
            })
            
        return holders
    except Exception as e:
        log.error(f"Failed to fetch holdings for ${ticker_symbol}: {e}")
        return None

def run():
    if not DB_PATH.exists():
        log.error(f"Database not found at {DB_PATH}")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    tickers = [t for t in master_data.keys() if master_data[t].get("human_research", {}).get("Bucket") != "Private"]
    log.info(f"Targeting {len(tickers)} tickers for institutional analysis.")

    updated_count = 0
    for ticker in tickers:
        yf_ticker = clean_ticker(ticker)
        holdings = fetch_inst_data(yf_ticker)
        
        if holdings:
            # Inject into master data
            if "human_research" not in master_data[ticker]:
                master_data[ticker]["human_research"] = {}
            
            master_data[ticker]["human_research"]["inst_13f_alpha"] = {
                "top_holders": holdings,
                "conviction_count": sum(1 for h in holdings if h["is_conviction"]),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            updated_count += 1
            log.info(f"  ✅ Updated ${ticker} | {len(holdings)} holders | {master_data[ticker]['human_research']['inst_13f_alpha']['conviction_count']} conviction")
        
        # Be nice
        time.sleep(2)

    if updated_count > 0:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(master_data, f, indent=4, ensure_ascii=True)
        log.info(f"Saved institutional alpha to {DB_PATH}")
        
        # Sync JS bridge
        JS_PATH = ROOT / "database" / "dashboard_data.js"
        if JS_PATH.exists():
            js_content = "window.CPO_MASTER_DATA = " + json.dumps(master_data, indent=2, ensure_ascii=True) + ";"
            JS_PATH.write_text(js_content, encoding="utf-8")
            log.info(f"Synced dashboard JS bridge.")

if __name__ == "__main__":
    run()
