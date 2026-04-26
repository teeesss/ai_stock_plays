import asyncio
import json
import random
from pathlib import Path

from curl_cffi import requests as cffi_requests

# Mirroring the setup from engine/live_prices.py
from live_prices import fetch_batch, get_valid_auth


class BridgeAuditor:
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.bridge_path = self.root / "database" / "ticker_name_map.json"

    async def audit_full_bridge(self):
        if not self.bridge_path.exists():
            print("[ERR] Bridge file not found.")
            return

        with open(self.bridge_path, "r", encoding="utf-8") as f:
            bridge = json.load(f)

        # Unique tradeable symbols from the bridge
        tickers = list(set(bridge.values()))
        print(f"[AUDIT] Starting stealth audit of {len(tickers)} symbols using mirrored engine...")

        # REPLICATE STEALTH HANDSHAKE
        cookie_dict, crumb, user_agent = await get_valid_auth()
        client = cffi_requests.Session(impersonate="chrome146")
        client.headers.update({"User-Agent": user_agent})
        client.cookies.update(cookie_dict)

        dead_tickers = []
        # For auditing 3,000+ items, we use bundles of 50 (middle ground for speed/stealth)
        bundle_size = 50
        chunks = [tickers[i : i + bundle_size] for i in range(0, len(tickers), bundle_size)]

        for i, chunk in enumerate(chunks):
            print(f"  [Probe] Batch {i+1}/{len(chunks)} ({len(chunk)} symbols)...")

            try:
                # Mirror the exact fetch_batch logic
                results = fetch_batch(chunk, client, crumb)

                # Identify symbols that returned an empty dict or no price
                for t in chunk:
                    entry = results.get(t, {})
                    if not entry or entry.get("price") is None:
                        dead_tickers.append(t)

            except Exception as e:
                print(f"    [!] Error in batch {i+1}: {e}")

            # Mirror the jitter behavior from the main engine
            delay = random.uniform(1.5, 3.0)
            await asyncio.sleep(delay)

        print("-" * 50)
        print("[RESULTS] Audit Complete.")
        print(f"  Analyzed: {len(tickers)}")
        print(f"  Functional: {len(tickers) - len(dead_tickers)}")
        print(f"  Dead:       {len(dead_tickers)}")
        print("-" * 50)

        if dead_tickers:
            results_path = self.root / "database" / "bridge_dead_tickers.json"
            # Reverse lookup name mapping for context
            name_map = {v: k for k, v in bridge.items()}
            full_report = {t: name_map.get(t, "Unknown") for t in dead_tickers}

            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(full_report, f, indent=2)

            print(f"[OK] Saved list of dead/misaligned symbols to: {results_path}")
            print(f"Top Offenders: {dead_tickers[:10]}")


if __name__ == "__main__":
    auditor = BridgeAuditor()
    asyncio.run(auditor.audit_full_bridge())
