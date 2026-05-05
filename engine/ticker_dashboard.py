import argparse
import asyncio
import datetime
import json
import os
import re
import smtplib
import sys
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Add engine to path for module discovery
sys.path.append(str(Path(__file__).parent))

# V28: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
except Exception as e:
    print(f"[!] Dependency Guardian Warning: {e}")

try:
    # Try direct imports first (standard for running from root)
    try:
        from live_prices import async_run_fetch
        from market_session import MarketSession
        from remote_sync import RemoteSync
        from ticker_utils import (
            extract_ticker_eps,
            get_authoritative_prev_close,
            get_header_timestamp,
            get_session_badge_style,
            get_ticker_session_data,
            render_valuation_row,
        )
    except ImportError:
        # Fallback to engine-prefixed imports
        from engine.live_prices import async_run_fetch
        from engine.market_session import MarketSession
        from engine.remote_sync import RemoteSync
        from engine.ticker_utils import (
            extract_ticker_eps,
            get_authoritative_prev_close,
            get_header_timestamp,
            get_session_badge_style,
            get_ticker_session_data,
            render_valuation_row,
        )
except ImportError as e:
    print(f"[!] FATAL: Could not import engine foundations: {e}")
    import traceback

    traceback.print_exc()

    # Minimal stubs (Emergency Fallback Only)
    def extract_ticker_eps(m, k):
        return None, None

    def get_authoritative_prev_close(p):
        return None

    def get_header_timestamp(d):
        return d.strftime("%m/%d/%Y %H:%M")

    def get_ticker_session_data(p, s, m):
        return 0, 0, ""

    def render_valuation_row(p, m, s):
        return []

    def get_session_badge_style(s):
        return "C", "#94a3b8"

    class RemoteSync:
        @staticmethod
        def sync_file(p):
            print(f"[!] Sync skipped: {p}")

    class MarketSession:
        def get_market_session_label(self, s):
            return ""

    async def async_run_fetch(**kwargs):
        return {}


class WatchlistReporter:
    def __init__(self, tickers_path, sort_mode=None):
        self.tickers_path = tickers_path
        self.sort_mode = sort_mode
        self.now = datetime.datetime.now()
        self.ms = MarketSession()
        self.db_path = Path("database")
        self.db_path.mkdir(exist_ok=True)

    async def run(self):
        # 1. Load Watchlist
        try:
            with open(self.tickers_path, "r", encoding="utf-8") as f:
                tickers = [line.strip().upper() for line in f if line.strip()]
        except Exception as e:
            # Fallback if tickers_path was a flag mistakenly interpreted as path
            if str(self.tickers_path).startswith("-"):
                tickers_file = "tickers.txt"
                with open(tickers_file, "r", encoding="utf-8") as f:
                    tickers = [line.strip().upper() for line in f if line.strip()]
            else:
                print(f"[ERR] Could not read tickers: {e}")
                return

        if not tickers:
            print("Empty watchlist.")
            return

        # 2. Fetch Fresh Data (Single Source of Truth)
        try:
            prices = await async_run_fetch(tickers=tickers, skip_sync=True)
        except Exception:
            try:
                with open("database/live_prices.json", "r", encoding="utf-8") as f:
                    prices = json.load(f)
            except:
                prices = {}

        master = {}
        master_path = Path("database/CPO_MASTER_DATA.json")
        if master_path.exists():
            try:
                with open(master_path, "r", encoding="utf-8") as f:
                    master = json.load(f)
            except:
                pass

        # 3. Process & Sort
        processed_tickers = []
        for sym in tickers:
            p = prices.get(sym, {})
            m = master.get(sym, {})

            # V30.5.1: Unified Session Pricing (Single Source)
            price, pct, sess = get_ticker_session_data(p, sym, self.ms)

            # Authoritative Anchor for Close %
            prev = get_authoritative_prev_close(p)
            c_p = p.get("close_price", 0)
            c_pct = 0
            if prev and c_p:
                c_pct = ((c_p / prev) - 1) * 100
            else:
                c_pct = p.get("change_pct", 0) or 0

            processed_tickers.append(
                {
                    "sym": sym,
                    "price": price,
                    "pct": pct,
                    "sess": sess,
                    "p_data": p,
                    "m_data": m,
                    "close_price": c_p,
                    "close_pct": c_pct,
                }
            )

        # Sort Logic (V30.6.9: Numerical High-to-Low)
        if self.sort_mode == "close":
            processed_tickers.sort(key=lambda x: x["close_pct"], reverse=True)
        elif self.sort_mode == "ext":
            processed_tickers.sort(key=lambda x: x["pct"], reverse=True)
        elif self.sort_mode == "momentum":
            # Numerical High to Low (not absolute value)
            processed_tickers.sort(key=lambda x: x["pct"], reverse=True)

        # 4. Render CLI Output
        print(f"\nREAL-TIME WATCHLIST (Sorted: {self.sort_mode or 'Default'})")
        for t in processed_tickers:
            row_str = f"${t['sym']}"
            if t["price"] > 0:
                row_str += f"\t${t['price']:,.2f} {t['sess']} {t['pct']:+.2f}%"
            else:
                row_str += "\tN/A"
            print(row_str)

            c_p = t["p_data"].get("close_price")
            c_pct = t["close_pct"]
            if c_p:
                print(f"C: ${c_p:,.2f} {c_pct:+.2f}%")

            val_parts = render_valuation_row(t["p_data"], t["m_data"], t["sym"])
            if val_parts:
                print(f"[ {' '.join(val_parts)} ]")

        # 5. Generate HTML & Deploy
        html = self.compose_html(processed_tickers)
        preview_path = (self.db_path / "tickers_preview.html").resolve()
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html)

        print("[*] Deploying to bmwseals.com/stocks/tickers.html...")
        RemoteSync.sync_file(preview_path)

        # 6. Send Email
        self.send_email(html)

    def compose_html(self, processed_tickers):
        rows = ""
        for t in processed_tickers:
            sym, price, pct, sess = t["sym"], t["price"], t["pct"], t["sess"]
            p, m = t["p_data"], t["m_data"]

            c_p = t["close_price"]
            c_pct = t["close_pct"]

            m_cap_val = p.get("market_cap") or m.get("financials", {}).get("marketCap") or 0
            val_parts = render_valuation_row(p, m, sym)

            # Map parts to columns: [MCap, P/E 26, P/E 27]
            cap_str, p26_str, p27_str = "N/A", "-", "-"
            for part in val_parts:
                if "MCap:" in part:
                    cap_str = part.replace("MCap:", "").strip()
                elif "'26 [" in part:
                    p26_str = part.replace("'26 [", "").replace("]", "").strip()
                elif "'27 [" in part:
                    p27_str = part.replace("'27 [", "").replace("]", "").strip()
                elif "P/E:" in part:
                    p26_str = part.replace("P/E:", "").strip()

            t_clr = "#4ade80" if pct >= 0 else "#f87171"
            c_clr = "#4ade80" if c_pct >= 0 else "#f87171"
            _, badge_color = get_session_badge_style(sess)

            rows += f"""
            <tr style="border-bottom:1px solid #1e293b;">
                <td style="padding:12px; font-weight:bold; color:#f8fafc;" data-v="{sym}">${sym}</td>
                <td style="padding:12px; font-family:monospace; color:{t_clr}; text-align:right;" data-v="{price}">${price:,.2f}</td>
                <td style="padding:12px; font-family:monospace; color:{badge_color}; text-align:center; font-size:10px; font-weight:bold;" data-v="{sess or 'C'}">{sess or 'C'}</td>
                <td style="padding:12px; font-family:monospace; color:{t_clr}; font-weight:bold; text-align:right;" data-v="{pct}">{pct:+.2f}%</td>
                <td style="padding:12px; font-family:monospace; color:#cbd5e1; text-align:right;" data-v="{c_p}">${c_p:,.2f}</td>
                <td style="padding:12px; font-family:monospace; color:{c_clr}; font-weight:bold; text-align:right;" data-v="{c_pct}">{c_pct:+.2f}%</td>
                <td style="padding:12px; font-family:monospace; color:#38bdf8; text-align:right;" data-v="{m_cap_val}">{cap_str}</td>
                <td style="padding:12px; font-family:monospace; color:#94a3b8; text-align:right;">{p26_str}</td>
                <td style="padding:12px; font-family:monospace; color:#94a3b8; text-align:right;">{p27_str}</td>
            </tr>"""

        html = f"""<!DOCTYPE html><html><head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background-color:#020617; color:#f8fafc; font-family:monospace; padding:10px; }}
                .container {{ max-width:1100px; margin:0 auto; background-color:#0f172a; border:1px solid #1e293b; border-radius:8px; overflow:hidden; }}
                table {{ width:100%; border-collapse:collapse; }}
                th {{ background-color:#1e293b; color:#64748b; font-size:10px; text-transform:uppercase; padding:12px; text-align:right; cursor:pointer; }}
                th:hover {{ color:#f59e0b; }}
                th.l {{ text-align:left; }}
                th.c {{ text-align:center; }}
                @media (max-width: 800px) {{
                    th:nth-child(5), td:nth-child(5), th:nth-child(7), td:nth-child(7), th:nth-child(8), td:nth-child(8), th:nth-child(9), td:nth-child(9) {{ display: none; }}
                }}
            </style>
            <script>
                function sortTable(n) {{
                    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                    table = document.getElementById("tBody");
                    switching = true; dir = "desc";
                    while (switching) {{
                        switching = false; rows = table.rows;
                        for (i = 0; i < (rows.length - 1); i++) {{
                            shouldSwitch = false;
                            let xAttr = rows[i].getElementsByTagName("TD")[n].getAttribute("data-v");
                            let yAttr = rows[i+1].getElementsByTagName("TD")[n].getAttribute("data-v");
                            let xV = isNaN(parseFloat(xAttr)) ? xAttr : parseFloat(xAttr);
                            let yV = isNaN(parseFloat(yAttr)) ? yAttr : parseFloat(yAttr);
                            if (dir == "desc") {{ if (xV < yV) {{ shouldSwitch = true; break; }} }}
                            else {{ if (xV > yV) {{ shouldSwitch = true; break; }} }}
                        }}
                        if (shouldSwitch) {{ rows[i].parentNode.insertBefore(rows[i + 1], rows[i]); switching = true; switchcount ++; }}
                        else {{ if (switchcount == 0 && dir == "desc") {{ dir = "asc"; switching = true; }} }}
                    }}
                }}
            </script>
        </head><body>
            <div class="container">
                <div style="padding:20px; border-bottom:2px solid #6366f1; text-align:center;">
                    <div style="font-size:22px; font-weight:900; color:#f59e0b; letter-spacing:2px;">WATCHLIST COCKPIT</div>
                    <div style="font-size:10px; color:#64748b; margin-top:5px;">{get_header_timestamp(self.now)} EST // INSTITUTIONAL FEED</div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th class="l" onclick="sortTable(0)">Ticker</th>
                            <th onclick="sortTable(1)">Price</th>
                            <th class="c" onclick="sortTable(2)">AH OVN PRE</th>
                            <th onclick="sortTable(3)">% CHG</th>
                            <th onclick="sortTable(4)">Close</th>
                            <th onclick="sortTable(5)">C %</th>
                            <th onclick="sortTable(6)">MCap</th>
                            <th onclick="sortTable(7)">'26 P/E</th>
                            <th onclick="sortTable(8)">'27 P/E</th>
                        </tr>
                    </thead>
                    <tbody id="tBody">{rows}</tbody>
                </table>
                <div style="padding:20px; text-align:center; font-size:10px; color:#475569; border-top:1px solid #1e293b;">
                    GIGACPO TICKER ENGINE // AUTHENTIC TRADING DATA
                </div>
            </div>
        </body></html>"""
        return re.sub(r">\s+<", "><", html).strip()

    def send_email(self, html):
        u, pk = os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASS")
        r = os.getenv("RECIPIENT_EMAIL", "rayjonesy@gmail.com")
        if not u or not pk:
            return

        msg = MIMEMultipart()
        msg["From"] = f"Ticker Intel <{u}>"
        msg["To"] = r
        msg["Subject"] = (
            f"Watchlist Intelligence // {self.now.strftime('%m/%d/%y')} [{uuid.uuid4().hex[:6]}]"
        )
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(u, pk)
                s.send_message(msg)
            print("[OK] WATCHLIST EMAIL DISPATCHED.")
        except Exception as e:
            print(f"[ERR] Email failed: {e}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tickers_file", nargs="?", default="tickers.txt")
    parser.add_argument("--sort-close", action="store_true")
    parser.add_argument("--sort-ext", action="store_true")
    parser.add_argument("--sort-mom", action="store_true")
    parser.add_argument(
        "--email", action="store_true", help="Send email (default is true in reporter)"
    )
    args = parser.parse_args()

    sort_mode = None
    if args.sort_close:
        sort_mode = "close"
    elif args.sort_ext:
        sort_mode = "ext"
    elif args.sort_mom:
        sort_mode = "momentum"

    reporter = WatchlistReporter(args.tickers_file, sort_mode=sort_mode)
    await reporter.run()


if __name__ == "__main__":
    asyncio.run(main())
