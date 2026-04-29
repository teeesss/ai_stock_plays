# V28: GIGACPO SOVEREIGN INTELLIGENCE ENGINE
import argparse
import asyncio
import datetime
import json
import logging
import os
import random
import re
import smtplib
import sys
import time

import requests

# V28: Hierarchy Leader Error Monitoring
try:
    import error_monitor
except ImportError:
    from engine import error_monitor
error_monitor.init_error_monitor()

try:
    from remote_sync import RemoteSync
except ImportError:
    from engine.remote_sync import RemoteSync

import hashlib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from curl_cffi import requests as cffi_requests
from dotenv import load_dotenv

# V28: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
    error_monitor.init_error_monitor()
except SystemExit:
    raise  # Let the dependency manager cleanly exit the process
except Exception as e:
    print(f"[!] Dependency Guardian Warning: {e}")

# Engine Foundations
try:
    from live_blog_scraper import LiveBlogScraper
    from live_prices import async_run_fetch
    from local_nlp import LocalIntelligenceSynthesizer
    from macro_aggregator import MacroAggregator
    from market_session import MarketSession
    from paywall_guardian import PaywallGuardian
    from paywall_intelligence import DeepScraper, PaywallIntelligence
except ImportError:
    from engine.email_spark_fetcher import run_spark_fetch
    from engine.live_blog_scraper import LiveBlogScraper
    from engine.live_prices import async_run_fetch
    from engine.local_nlp import LocalIntelligenceSynthesizer
    from engine.macro_aggregator import MacroAggregator
    from engine.market_session import MarketSession
    from engine.paywall_guardian import PaywallGuardian
    from engine.paywall_intelligence import DeepScraper, PaywallIntelligence

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)
load_dotenv()


class SovereignIntelligenceEngine:
    """
    GIGACPO SOVEREIGN INTELLIGENCE V4.3
    Aesthetics: Brand-Hardened (Blue/Gold/Green/Red)
    Logic: Global Macro Synthesis + Ticker Injection
    """

    def __init__(self):
        def ts():
            return datetime.datetime.now().strftime("%H:%M:%S")

        print(f"[{ts()}] [DEBUG] Constructor: Setting paths...")
        self.root = Path(__file__).parent.parent
        self.db_path = self.root / "database"
        self.web_root = self.root / "web"

        # V23.58: Timezone-Aware Pulse
        # Normalizing to US/Eastern for consistent session tagging across VM/Server/Desktop
        self.now = self._get_est_now()

        # Design Tokens
        self.COLOR_BG = "#020617"
        self.COLOR_CARD = "#0f172a"
        self.COLOR_LITE_BLUE = "#0ea5e9"
        self.COLOR_GOLD = "#f59e0b"
        self.COLOR_GREEN = "#10b981"
        self.COLOR_DANGER = "#f43f5e"
        self.COLOR_TEXT = "#f8fafc"
        self.COLOR_DIM = "#64748b"

        # V22.7: Load massive symbol bridge
        print(f"[{ts()}] [DEBUG] Constructor: Loading ticker_name_map.json...")
        start = time.time()
        self.ticker_name_map = self._load_json("ticker_name_map.json")
        elapsed = time.time() - start
        print(
            f"[{ts()}] [DEBUG] Constructor: Map loaded ({len(self.ticker_name_map)} entries) in {elapsed:.2f}s."
        )

        # V26.14: Hierarchy Leader Initialization
        self.market_session = MarketSession()

    def _get_est_now(self):
        """Returns the current time normalized to US/Eastern (EDT/EST) anchored to UTC."""
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        try:
            from zoneinfo import ZoneInfo

            return now_utc.astimezone(ZoneInfo("US/Eastern"))
        except:
            # Fallback for systems without zoneinfo
            return now_utc - datetime.timedelta(hours=4)

    # V22.5: Centralized High-Confidence Aliases (Names to Tickers)
    ALIAS_MAP = {
        "NVIDIA": "NVDA",
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "AMAZON": "AMZN",
        "APPLE": "AAPL",
        "MICROSOFT": "MSFT",
        "META": "META",
        "FACEBOOK": "META",
        "TESLA": "TSLA",
        "BROADCOM": "AVGO",
        "MARVELL": "MRVL",
        "TSMC": "TSM",
        "TAIWAN SEMI": "TSM",
        "ARM HOLDINGS": "ARM",
        "NOKIA": "NOK",
        "AMKOR": "AMKR",
        "NXP": "NXPI",
        "AXT": "AXTI",
        "CAMTEK": "CAMT",
        "SYNOPSYS": "SNPS",
        "MACOM": "MTSI",
        "VIAVI": "VIAV",
        "SIFIVE": "NVDA",
        "KLA": "KLAC",
        "J.P. MORGAN": "JPM",
        "CIBC": "CM",
        "ROYAL BANK": "RY",
        "RBC": "RY",
        "BMW": "BMWYY",
        "ASE": "ASX",
        "IPG": "IPGP",
        "ASMPT": "0522.HK",
    }

    def _load_aliases(self):
        """Merges manual high-fidelity aliases with the auto-generated 1,931-item brand bridge."""
        merged = self.ALIAS_MAP.copy()
        try:
            brand_bridge = self._load_json("name_aliases.json")
            merged.update(brand_bridge)
        except:
            pass
        return merged

    def is_legit_ticker(self, t):
        if not t or not isinstance(t, str):
            return False
        t = t.upper()
        if len(t) < 2 or t.isdigit():
            return False

        # V22.93: High-Fidelity Noise Shield
        # Filter company names or noise accidentally being treated as tickers
        if any(x in t for x in [" ", "/", "\\", "(", ")", ".", ",", ":", "'", '"']):
            return False

        # Mandatory 2-Letter Whitelist (Filters out IN, OF, TO, BY, etc.)
        if len(t) == 2:
            WHITELIST_2 = {
                "BA",
                "GM",
                "GE",
                "MU",
                "FN",
                "V",
                "MA",
                "T",
                "F",
                "KO",
                "VZ",
                "PYPL",
                "UBER",
                "LYFT",
            }
            return t in WHITELIST_2

        # Financial Acronym & Intelligence Blacklist
        FETCH_BLACKLIST = {
            "AI",
            "US",
            "NYSE",
            "NASDAQ",
            "ITS",
            "OSAT",
            "POS",
            "AND",
            "RESEPI",
            "NASA",
            "EUV",
            "ESA",
            "PT",
            "PTO",
            "M1",
            "M2",
            "M3",
            "G1",
            "G2",
            "G3",
            "G5",
            "YTD",
            "HELOC",
            "APY",
            "APR",
            "PE",
            "EPS",
            "ROE",
            "ROIC",
            "EBITDA",
            "GAAP",
            "CFO",
            "COO",
            "CEO",
            "CTO",
            "IPO",
            "LBO",
            "PFIC",
            "FATCA",
            "ETF",
            "IRA",
            "HSA",
            "RAN",
            "EMS",
            "LIDE",
            "HBM",
            "DRAM",
            "NAND",
            "CPO",
            "GPU",
            "CPU",
            "NPU",
            "LSA",
            "NLP",
            "AIAI",
            "S&P",
            "DJI",
            "SNP",
            "QQQ",
            "CD",
            "EST",
            "MARKET",
            "FED",
            "CPI",
            "PPI",
            "GDP",
            "USD",
            "EUR",
            "GBP",
            "JPY",
            "CAD",
            "USDC",
            "USDT",
            "DAI",
            "BUSD",
            "PYUSD",
            "TETHER",
            "STABLECOINS",
            "FDUSD",
            "FORM",
            "ON",
            "AT",
            "BY",
            "IF",
            "SO",
            "ME",
            "IT",
            "IS",
            "AS",
            "BE",
            "AN",
            "OR",
            "OF",
            "TO",
            "IN",
        }
        return t not in FETCH_BLACKLIST

    def _load_json(self, name):
        p = self.db_path / name
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _save_json(self, name, data):
        p = self.db_path / name
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            # Duplicate to .js for web terminal
            js_p = self.db_path / name.replace(".json", ".js")
            with open(js_p, "w", encoding="utf-8") as f:
                f.write(f"const LIVE_PRICES = {json.dumps(data, indent=2)};")
            return True
        except:
            return False

    def is_market_active(self):
        # V26.14: Defer to Hierarchy Leader
        return self.market_session.is_market_active()

    def is_entity_fresh(self, t, prices):
        """Global 15-minute TTL check (V22.7)"""
        existing = prices.get(t, {})
        if not existing or existing.get("price") is None:
            return False

        ts = existing.get("timestamp", 0)
        now = time.time()

        # V22.7: Strict 15-Minute Global TTL Bypass
        # If the market is active (Regular, Extended, or Futures) OR asset is Crypto -> 15m rule
        if self.is_market_active() or "USD" in t:
            return (now - ts) < 900  # 15 min check (Global)

        # Weekend / Middle-of-Night Stasis (Market Dead) -> Fresh from memory
        # This anchors Friday close prices til Sunday Night Futures open.
        return True

    def fetch_sentiment(self):
        market_val = 50
        crypto_val = 50
        try:
            r = cffi_requests.get(
                "https://feargreedmeter.com/", impersonate="chrome146", timeout=10
            )
            m = re.findall(r"<div[^>]*>(\d+)</div>", r.text)
            if m:
                market_val = int(m[0])
        except:
            pass
        try:
            r = cffi_requests.get(
                "https://feargreedmeter.com/crypto", impersonate="chrome146", timeout=10
            )
            m = re.findall(r"<div[^>]*>(\d+)</div>", r.text)
            if m:
                crypto_val = int(m[0])
        except:
            pass

        def label(v):
            if v <= 25:
                return "EXTREME FEAR"
            if v <= 45:
                return "FEAR"
            if v <= 55:
                return "NEUTRAL"
            if v <= 75:
                return "GREED"
            return "EXTREME GREED"

        return {
            "market": {"value": market_val, "label": label(market_val)},
            "crypto": {"value": crypto_val, "label": label(crypto_val)},
        }

    def is_shite_ticker(self, sym):
        """V23.01: Aggressive Stablecoin and Fake-Ticker Purge."""
        if not sym:
            return True
        t_up = sym.upper()
        # Stablecoin list
        if any(
            sc in t_up
            for sc in [
                "USDC",
                "USDT",
                "TETHER",
                "STABLECOIN",
                "DAI",
                "BUSD",
                "PYUSD",
                "CIRCLE",
                "FDUSD",
            ]
        ):
            return True
        # Generic noise
        if t_up in ["YAHOO", "BREAKING", "NEWS", "STOCK", "MARKET"]:
            return True
        return False

    def fetch_live_macro(self):
        # V22.96: Prioritized Multi-Stream News Engine (Triple-Feed V3.1)
        FEEDS = [
            ("https://finance.yahoo.com/rss/topic/analysis", 30),
            ("https://finance.yahoo.com/rss/topic/economic-news", 20),
            ("https://finance.yahoo.com/rss/topic/stock-market-news", 10),
        ]

        # Blacklist/Multipliers
        BLACKLIST = [
            "jim cramer",
            "mad money",
            "motley fool",
            "zacks",
            "investorplace",
            "simply wall st",
            "benzinga",
            "david einhorn",
        ]
        # Tier 1 (+50): High-Impact Volatility/Geopolitics
        URGENT = [
            "war",
            "iran",
            "israel",
            "conflict",
            "missile",
            "strike",
            "emergency",
            "oil",
            "crude",
            "brent",
            "energy",
            "geopolitical",
        ]
        # Tier 2 (+40): Macro Indicators
        MACRO = [
            "jobs report",
            "unemployment",
            "nfp",
            "payrolls",
            "cpi",
            "inflation",
            "fed",
            "powell",
            "rate hike",
            "rate cut",
        ]
        # Tier 3 (+30): Corporate/Earning Highlights
        CORP = [
            "earnings",
            "beat",
            "miss",
            "eps",
            "revenue",
            "guidance",
            "buyback",
            "m&a",
            "acquisition",
        ]

        headlines = []
        seen_urls = set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Load master keys for Ticker Match boost (+20)
        master_keys = set()
        try:
            m_data = self._load_json("CPO_MASTER_DATA.json")
            master_keys = set(m_data.keys())
        except:
            pass

        for url, base_score in FEEDS:
            try:
                # Stealth Jitter: Prevent 429 via staggered bursts
                time.sleep(random.uniform(1.2, 3.1))
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    print(f"[RSS WARN] {url} returned {r.status_code}")
                    continue

                items = re.findall(r"<item>(.*?)</item>", r.text, re.DOTALL)
                for item in items:
                    t_match = re.search(r"<title>(.*?)</title>", item)
                    l_match = re.search(r"<link>(.*?)</link>", item)
                    d_match = re.search(r"<description>(.*?)</description>", item, re.DOTALL)

                    if t_match and l_match:
                        t = (
                            t_match.group(1)
                            .replace("&apos;", "'")
                            .replace("&quot;", '"')
                            .replace("<![CDATA[", "")
                            .replace("]]>", "")
                        )
                        url = l_match.group(1).replace("<![CDATA[", "").replace("]]>", "")

                        # Dedup & Blacklist
                        if url in seen_urls:
                            continue
                        t_lower = t.lower()
                        if any(b in t_lower for b in BLACKLIST):
                            continue

                        # SCORING (V3.1 Impact Matrix)
                        score = base_score
                        if any(k in t_lower for k in URGENT):
                            score += 50
                        if any(k in t_lower for k in MACRO):
                            score += 40
                        if any(k in t_lower for k in CORP):
                            score += 30

                        # Ticker Match (+20) - Fast set check
                        words = set(re.findall(r"\b[A-Z]{2,6}\b", t))
                        if words.intersection(master_keys):
                            score += 20

                        d = ""
                        if d_match:
                            d = d_match.group(1).replace("<![CDATA[", "").replace("]]>", "")
                            d = re.sub(r"<.*?>", "", d)  # Strip HTML
                            d = re.sub(r"Read more on Yahoo Finance.*", "", d).strip()

                        headlines.append({"title": t, "link": url, "summary": d, "score": score})
                        seen_urls.add(url)
            except Exception as e:
                print(f"[RSS ERR] {url}: {e}")

        # Top 15 Final Ranking
        headlines.sort(key=lambda x: x["score"], reverse=True)
        return headlines[:15]

    async def fetch_agg(self):
        """Aggregates and scores news with hardening/stealth protocols."""
        # V23.61: 15-minute Cache Enforcement
        pass

    async def fetch_priority_signals(self):
        """V23.55: Surgical harvest for high-alpha tech priority tickers/keywords."""
        ROOT = Path(__file__).parent.parent
        PATH = ROOT / "priority_tickers.txt"
        if not PATH.exists():
            return []

        tickers = []
        with open(PATH, "r") as f:
            for line in f:
                t = line.strip()
                if t:
                    tickers.append(t)

        if not tickers:
            return []

        print(f"[INTEL] Starting Priority Harvest for {len(tickers)} targets...")
        try:
            from engine.news_fetcher import YahooNewsFetcher
        except ImportError:
            from news_fetcher import YahooNewsFetcher

        fetcher = YahooNewsFetcher()
        # Days=2 for extreme freshness in priority block
        raw_results = await fetcher.fetch_batch(tickers, days=2)

        priority_headlines = []
        seen_urls = set()

        # Scoring logic for priority section
        for target, stories in raw_results.items():
            for s in stories:
                url = s.get("link") or s.get("url")
                if not url or url in seen_urls:
                    continue

                title = s.get("title", "")
                # Base Priority Score
                score = 250

                # Cross-Ticker Match Discovery (+100)
                # If target is MRVL, and title mentions GOOGL/GOOGLE
                t_lower = title.lower()
                matches = re.findall(r"\b[A-Z]{2,6}\b", title)
                if len(set(matches)) > 1:
                    score += 100

                # Keyword Boost (+50)
                if any(
                    k in t_lower
                    for k in [
                        "photonics",
                        "cpo",
                        "co-packaged",
                        "interconnect",
                        "chiplet",
                    ]
                ):
                    score += 50

                priority_headlines.append(
                    {
                        "title": title,
                        "link": url,
                        "summary": s.get("summary", ""),
                        "score": score,
                        "is_priority": True,
                        "target": target,
                    }
                )
                seen_urls.add(url)

        priority_headlines.sort(key=lambda x: x["score"], reverse=True)
        return priority_headlines[:10]

    def get_market_session(self, symbol=None, dt_override=None):
        # V26.14: Defer to Hierarchy Leader
        label = self.market_session.get_market_session_label(symbol, dt_override)
        # Convert 'CLOSED' back to empty string for legacy compatibility in email logic
        return label if label != "CLOSED" else ""

    def get_session_data(self, p_data, symbol=None):
        """Unified session logic: extract correct price/pct from live_prices schema."""
        sess = self.get_market_session(symbol)
        effective_sess = sess
        price = p_data.get("price", 0)
        pct = p_data.get("change_pct", 0)

        ext_type = p_data.get("ext_type")
        # High-Fidelity: Link data to session
        if ext_type and ext_type in ["OVN", "PRE", "POST", "AH"]:
            # Prioritize matching session
            match = ext_type == sess
            # Aliases for same session (POST == AH, PRE == PM/PRE, OVN matches AH/POST residues)
            if not match:
                match = (
                    (sess == "AH" and ext_type in ["POST", "AH"])
                    or (sess == "PRE" and ext_type == "PRE")
                    or (sess == "OVN" and ext_type in ["POST", "AH", "OVN"])
                )

            # V23.80: OVN Fallback — If we are in PRE (4AM-9:30AM) but only have OVN data, use OVN
            if not match and sess == "PRE" and ext_type == "OVN":
                match = True

            # V28: Atomic override to prevent mixed state ($REG + %EXT)
            # We only override if it's a confirmed session match OR if the data is explicitly LIVE
            if match:
                e_p = p_data.get("ext_price")
                e_pct = p_data.get("ext_pct")

                if e_p is not None:
                    price = e_p
                    prev = p_data.get("close_price") or p_data.get("prev_close")
                    if prev:
                        pct = ((price / prev) - 1) * 100
                    elif e_pct is not None:
                        pct = e_pct

                    # V24.7: Data-Driven Labeling. If we scavenged AH data during OVN, label it AH.
                    lbl = ext_type
                    if lbl == "POST":
                        lbl = "AH"
                    effective_sess = lbl
            elif sess == "LIVE":
                effective_sess = "LIVE"
            else:
                # If no match in an extended session, return CLOSED if not in REG
                effective_sess = "CLOSED"

        return price, pct, effective_sess

    def get_session_tag_html(self, fs="8px", sess_override=None, color=None):
        sess = sess_override if sess_override else ""
        if not sess:
            return ""

        # Standardize
        if sess == "PM":
            sess = "PRE"
        if sess == "POST":
            sess = "AH"

        if sess == "LIVE":
            return f'<span class="sess-badge sess-live" style="font-size:{fs};">L<span style="color:#10b981;">⚡</span></span>'

        return f'<span class="sess-badge sess-{sess.lower()}" style="font-size:{fs};">{sess}</span>'

    def get_context_icon(self, title, used_icons=None):
        """V23.60: Context-aware icon selection with deep rotation and de-duplication."""
        t = title.lower()

        # Priority mapping: Keyword -> Icon Pool (Expanded for 100% variety)
        mapping = [
            (
                [
                    "war",
                    "iran",
                    "israel",
                    "conflict",
                    "missile",
                    "attack",
                    "strike",
                    "defense",
                    "military",
                    "1930s",
                    "pentagon",
                    "strike",
                ],
                ["🛡️", "⚔️", "🛰️", "🪖", "🎯", "⚓"],
            ),
            (
                [
                    "oil",
                    "energy",
                    "fuel",
                    "shuttering",
                    "hormuz",
                    "crude",
                    "gas",
                    "gasoline",
                    "power grid",
                    "nuclear",
                ],
                ["🛢️", "⚡", "🔥", "☢️", "🔌", "🌋"],
            ),
            (
                [
                    "fed",
                    "rate",
                    "powell",
                    "inflation",
                    "cpi",
                    "jobs",
                    "yield",
                    "budget",
                    "debt",
                    "economy",
                    "recession",
                    "unemployment",
                ],
                ["⚖️", "📉", "🏛️", "📋", "🏢", "🏘️", "🕰️"],
            ),
            (
                [
                    "ai ",
                    "chip",
                    "nvidia",
                    "broadcom",
                    "semiconductor",
                    "mrvl",
                    "amd",
                    "quantum",
                    "robotics",
                    "hbm",
                    "foundry",
                    "gpu",
                ],
                ["🧠", "🤖", "📟", "💾", "🔌", "⚙️", "🔬"],
            ),
            (
                [
                    "earnings",
                    "revenue",
                    "quarterly",
                    "profit",
                    "dividend",
                    "guidance",
                    "record high",
                    "market today",
                    "stocks fall",
                    "stocks rise",
                    "shares leap",
                    "beat",
                ],
                ["📈", "📊", "🎯", "💎", "💰", "🏆", "🌟"],
            ),
            (
                [
                    "software",
                    "cloud",
                    "saas",
                    "meta",
                    "google",
                    "apple",
                    "amazon",
                    "tech",
                    "online",
                    "data center",
                    "network",
                ],
                ["💻", "🌐", "☁️", "📱", "📡", "🖱️", "🖲️"],
            ),
            (
                [
                    "lawsuit",
                    "sec",
                    "investigation",
                    "regulation",
                    "agenda",
                    "trump",
                    "administration",
                    "policy",
                    "doj",
                    "court",
                ],
                ["📜", "🔨", "🗳️", "⚖️", "📢", "🖋️"],
            ),
            (
                [
                    "bitcoin",
                    "crypto",
                    "btc",
                    "eth",
                    "sol",
                    "coinbase",
                    "aave",
                    "ledger",
                    "stablecoin",
                    "defi",
                ],
                ["🪙", "🔗", "💎", "👾", "🕸️", "🗝️"],
            ),
            (
                [
                    "scam",
                    "fake",
                    "gold",
                    "romance",
                    "pig-butchering",
                    "theft",
                    "stole",
                    "fraud",
                    "hacking",
                    "cyber",
                ],
                ["🕵️", "🔐", "🚨", "🚫", "👺", "👤"],
            ),
            (
                [
                    "millionaire",
                    "wealth",
                    "save",
                    "money",
                    "investing",
                    "math",
                    "portfolio",
                    "fund",
                ],
                ["💰", "💵", "🏦", "💳", "🛒", "🛍️"],
            ),
            (
                [
                    "export",
                    "truck",
                    "logistic",
                    "border",
                    "shipping",
                    "freight",
                    "supply chain",
                    "cargo",
                ],
                ["🚛", "📦", "🚢", "🛫", "🚆", "⚓"],
            ),
            (
                [
                    "photonics",
                    "cpo",
                    "fiber",
                    "laser",
                    "connectivity",
                    "optical",
                    "bandwidth",
                ],
                ["📡", "✨", "📶", "⚡", "🌈", "📽️"],
            ),
        ]

        selected_icon = None
        for keywords, pool in mapping:
            if any(w in t for w in keywords):
                if used_icons is not None:
                    unused = [i for i in pool if i not in used_icons]
                    selected_icon = random.choice(unused) if unused else random.choice(pool)
                else:
                    selected_icon = random.choice(pool)
                break

        if not selected_icon:
            # Neutral rotation pool (Massively expanded)
            pool = [
                "📡",
                "🛰️",
                "🔭",
                "🔬",
                "🪐",
                "🌠",
                "🔮",
                "🧬",
                "🧪",
                "⚙️",
                "🛠️",
                "📡",
                "🛰️",
            ]
            if used_icons is not None:
                unused = [i for i in pool if i not in used_icons]
                selected_icon = random.choice(unused) if unused else random.choice(pool)
            else:
                selected_icon = random.choice(pool)

        if used_icons is not None:
            used_icons.add(selected_icon)
        return selected_icon

    def generate_sparkline_svg(self, points, color="#10b981", width=60, height=20):
        """DEPRECATED: Removed per user request."""
        return ""

    def get_ticker_chip(self, symbol, prices, simple=False, link=True):
        if symbol.startswith("$"):
            symbol = symbol[1:]
        p = prices.get(symbol)
        gold = self.COLOR_GOLD

        # Neutralize auto-linking for international symbols (LPK.DE -> LPK.&#8203;DE)
        display_sym = symbol
        if not link and "." in display_sym:
            display_sym = display_sym.replace(".", ".&#8203;")

        if not p or (p.get("price") is None and p.get("ext_price") is None):
            style = f"color:{gold}; font-weight:bold; text-decoration:none;"
            if simple:
                return f'<span style="{style}">{display_sym}</span>'
            return f'<span style="{style}">${display_sym}</span>'

        price, pct, sess = self.get_session_data(p, symbol)
        color = self.COLOR_GREEN if pct >= 0 else self.COLOR_DANGER
        emoji = "🟢" if pct >= 0 else "🔴"

        sess_tag = self.get_session_tag_html(fs="8px", sess_override=sess)

        anchor = ""
        if sess in ["PRE", "AH", "OVN", "POST"]:
            c_p = p.get("close_price") or p.get("price")
            if c_p:
                anchor = f'<span style="font-size:9px; color:#94a3b8; font-weight:normal;">&nbsp;| C: ${c_p:,.2f}</span>'

        style = f"color:{gold}; font-weight:bold; text-decoration:none;"
        pct_style = f"color:{color}; font-weight:800; text-decoration:none;"

        if simple:
            return f'<span style="{style}">{display_sym}</span>&nbsp;<span style="color:#cbd5e1; font-size:11px;">${price:.2f}</span>&nbsp;<span style="{pct_style}">{pct:+.2f}%{sess_tag}{anchor}</span>'
        return f'<span style="{style}">${display_sym}</span>&nbsp;<span style="color:#cbd5e1; font-size:12px;">${price:.2f}</span>&nbsp;<span style="{pct_style}">{emoji}&nbsp;{pct:+.2f}%{sess_tag}{anchor}</span>'

    def _fetch_ancillary_prices(self, tickers, prices):
        """V22.9: Hardened discovery hydration with 15m Global TTL bypass."""
        if not tickers:
            return {}
        # V22.54: Hardened remapping for common crypto/OTC aliases
        remapped = []
        for t in tickers:
            if not self.is_legit_ticker(t):
                continue

            # Map aliases
            final_t = t
            if t == "ADA":
                final_t = "ADA-USD"
            elif t == "BMWYY":
                final_t = "BMW.DE"

            # V22.9: STRICT 15M WAIT before discovery fetch
            if self.is_entity_fresh(final_t, prices):
                ts = prices.get(final_t, {}).get("timestamp", 0)
                age = int(time.time() - ts) // 60
                print(f"[CACHE] Discovery Fresh: {final_t} ({age}m old) - Skip fetch.")
                continue

            remapped.append(final_t)

        if not remapped:
            return {}
        try:
            print(f"[INTEL] discovery hydration required for {len(remapped)} assets...")
            new_prices = asyncio.run(
                async_run_fetch(tickers=remapped, dry_run=False, skip_sync=False)
            )
            return new_prices
        except Exception as e:
            print(f"[ERR] Ancillary fetch failed: {e}")
            return {}

    def inject_price_flair(self, text, prices, master=None, link=True):
        """High-density utility to inject real-time price info into headlines."""
        if not text:
            return text

        # V23.96: Absolute Isolation Logic
        words = text.split()
        for i, word in enumerate(words):
            # Strip punctuation to find the core ticker candidate
            stripped = word.strip(".,;:()$ '\"?!")
            if not stripped:
                continue
            clean_word = stripped.upper()

            # Check if it's a legit ticker we have price data for
            if clean_word in prices and self.is_legit_ticker(clean_word):
                p_data = prices[clean_word]
                price, pct, sess = self.get_session_data(p_data, clean_word)
                if price is None or pct is None:
                    continue

                color = "#22c55e" if pct >= 0 else "#ef4444"
                sign = "+" if pct >= 0 else ""
                sess_tag = self.get_session_tag_html(fs="8px", sess_override=sess)

                anchor = ""
                if sess in ["PRE", "AH", "OVN", "POST"]:
                    c_p = p_data.get("close_price") or p_data.get("price")
                    if c_p:
                        anchor = f' <span style="font-size:8px; color:#94a3b8; font-weight:normal;">| C: ${c_p:,.2f}</span>'

                # Reconstruction to prevent internal word corruption (e.g. "semiconductor")
                # We find the exact position of the stripped part to preserve surrounding punctuation
                start_idx = word.find(stripped)
                prefix = word[:start_idx].replace("'", "").replace('"', "").replace("`", "")
                suffix = (
                    word[start_idx + len(stripped) :]
                    .replace("'", "")
                    .replace('"', "")
                    .replace("`", "")
                )

                flair = f'{prefix}<strong>{stripped}</strong>&nbsp;(<span style="color:{color}; font-weight:bold;">${price:,.2f}&nbsp;{sign}{pct:.1f}%{sess_tag}{anchor}</span>){suffix}'
                words[i] = flair
                # Only flair the first high-confidence match per headline
                return " ".join(words)
        return text

    def synthesize_dossier(self, news_db, prices, master_data, sentiment):
        nlp = LocalIntelligenceSynthesizer()
        nlp.update_vibe_lexicon(sentiment)
        gold = "#f59e0b"
        text_bright = "#f8fafc"
        accent = "#60a5fa"

        agg = MacroAggregator()
        macro_headlines = asyncio.run(agg.fetch_agg())

        # V28: Specialized Source Detection (Hierarchy Leader)
        semi_sources = [
            "SemiAnalysis",
            "SemiEngineering",
            "Semiconductor Today",
            "EE Times Semi",
            "Semiconductor Digest",
            "SemiWiki",
            "IEEE Spectrum Semi",
            "Google News CPO Photonics",
            "Google News Semiconductors",
            "Google News Transceiver",
        ]

        print(
            f"[INFO] NLP Processor: Analyzing {len(macro_headlines)} headlines for institutional relevance..."
        )
        # Real-world NLP Intelligence Synthesis for Executive Summary
        # V24.9: mandatory 15 articles in list, increase ranking depth
        best_headlines = nlp.rank_news_relevance(
            macro_headlines, top_n=400, specialized_sources=semi_sources
        )

        if best_headlines:
            top_t = best_headlines[0].get("title", "Unknown")
            print(f"[INFO] [ALPHA] Lead Intelligence: {top_t[:70]}...")

        m_fg = int(sentiment.get("market", {}).get("value", 50))
        vibe_status = (
            "NEUTRAL / CHOPPY"
            if 40 <= m_fg <= 60
            else ("RISK-ON / ACCUMULATING" if m_fg > 60 else "RISK-OFF / PROTECTING")
        )

        # 3. Intelligent Narrative Synthesis (JIT Scrape + NLP)
        scraper = LiveBlogScraper()
        scraped_lead, lead_url = asyncio.run(scraper.get_sovereign_narrative())
        if scraped_lead:
            print(f"[MACRO] Scraped Live Narrative: {lead_url}")

        intel_text, used_links = nlp.synthesize_market_narrative(
            best_headlines, vibe_status, scraped_lead=scraped_lead
        )

        # V29.0: Institutional Deep-Fetch (Top 5 Alpha Articles)
        paywall_sources = ["bloomberg.com", "wsj.com", "barrons.com", "seekingalpha.com", "ft.com"]
        deep_fetch_tasks = []
        for i, art in enumerate(best_headlines[:5]):
            domain = PaywallIntelligence.get_domain(art.get("link", ""))
            if domain in paywall_sources:
                print(f"[INFO] [DEEP-FETCH] Harvesting full intelligence: {domain}")
                deep_fetch_tasks.append(art)

        if deep_fetch_tasks:

            async def do_deep_fetches(tasks):
                for art in tasks:
                    full_text = await DeepScraper.fetch_full_content(art.get("link"))
                    if full_text:
                        art["deep_content"] = full_text

            asyncio.run(do_deep_fetches(deep_fetch_tasks))

        # Institutional Summary Layout - Standardized with primary header classes (V23.72)
        summary_hdr_style = f"color:{text_bright}; font-size:42px; font-weight:900; letter-spacing:-1.5px; text-transform:uppercase; line-height:1.1; margin-bottom:12px;"

        # V29.0: Access Tip Header
        access_tip = (
            '<div style="text-align:center; margin-bottom:20px; font-size:12px; color:#94a3b8; border:1px solid rgba(148,163,184,0.2); padding:8px; border-radius:4px;">'
            "🚀 <strong>Intelligence Upgrade:</strong> To bypass institutional paywalls on the links below, install the "
            '<a href="https://gitflic.ru/project/magnolia1234/bypass-paywalls-chrome-clean" style="color:#38bdf8; text-decoration:none;">Bypass Paywalls Extension</a>.'
            "</div>"
        )

        if intel_text:
            # V28.8: Structured Intelligence Strip Rendering
            vibe = intel_text.get("vibe", "Neutral")
            focal = intel_text.get("focal_point", "General")
            points = intel_text.get("points", [])

            lead_vibe_html = (
                f"<strong>Sovereign Cycle: {vibe}</strong>. <em>Primary focal point: {focal}.</em>"
            )

            rows_html = ""
            for i, pt in enumerate(points):
                # V28.8: High-Contrast Alternating Intelligence Strips
                # Row A: Subtle Blue Tint / Row B: Minimalist Translucent
                bg = "rgba(56,189,248,0.06)" if i % 2 == 0 else "rgba(255,255,255,0.02)"

                # Apply high-density price flair to each bullet
                flaired_pt = self.inject_price_flair(pt, prices, master_data)

                rows_html += (
                    f'<div style="background:{bg}; padding:10px 14px; margin-bottom:2px; border-radius:4px; border-left:3px solid {accent if i % 2 == 0 else "rgba(99,102,241,0.1)"};">'
                    f'<span style="color:{text_bright}; font-size:15px; line-height:1.5;">&bull; {flaired_pt}</span>'
                    f'</div>'
                )

            # V28.8: Branded Divider (clean separation from news list)
            # V28.8: Mirrored Global Pulse header for Live News
            divider = f'<div class="section-hdr" style="text-align:center; color:{accent}; border-bottom:2px solid {accent}; margin:35px 0 20px 0; width:100%;">LIVE NEWS UPDATES</div>'

            exec_summary = f'{access_tip}<div class="hdr-title" style="{summary_hdr_style}">EXECUTIVE SUMMARY: <span style="color:{accent};">INTEL</span></div><div style="font-size:16px; color:{text_bright}; line-height:1.6; margin-bottom:15px;">{lead_vibe_html}</div><div style="margin-bottom:20px;">{rows_html}</div>{divider}'
        else:
            exec_summary = f'{access_tip}<div class="hdr-title" style="{summary_hdr_style}">EXECUTIVE SUMMARY: <span style="color:{accent};">INTEL</span></div><div style="font-size:16px; color:{text_bright}; line-height:1.6;">The session is carving out a {vibe_status} posture (F&G: {m_fg}). Liquidity is shifting across tech sectors.</div>'

        # V23.91: Cross-Section Deduplication
        # 4. Prune corpus for the supporting list (remove items used in narrative)
        # If we have a lead_url, ensure it's "used" if it matches anything in the corpus
        if lead_url:
            for art in best_headlines:
                if art.get("link") == lead_url:
                    used_links.add(lead_url)

        # V24.9: Increased capacity to ensure 15+ articles
        pruned_news = [art for art in best_headlines if art.get("link") not in used_links][:400]

        # V25.0: Rotation Engine - Prioritize fresh news, fallback to stale
        sent_news_path = Path("database/sent_news_history.json")
        sent_news_history = {}
        now_ts = time.time()
        if sent_news_path.exists():
            try:
                with open(sent_news_path, "r", encoding="utf-8") as f:
                    sent_news_history = json.load(f)
                    # Keep only last 24h
                    sent_news_history = {
                        k: v for k, v in sent_news_history.items() if (now_ts - v) < 86400
                    }
            except Exception:
                pass

        # V28: Unified Intelligence Sort (Replacing binary Fresh/Stale rotation)
        # Instead of a hard split that forces junk to the top, use a freshness bonus.
        # This keeps high-signal articles at the top while still favoring new info for variety.
        for art in pruned_news:
            # Baseline score
            score = art.get("final_score", 0)
            # Add +10 bonus if NOT sent in last 24h
            if art.get("link") not in sent_news_history:
                score += 10.0
            art["rotated_score"] = score

        rotated_news = sorted(pruned_news, key=lambda x: x.get("rotated_score", 0), reverse=True)

        fresh_count = sum(1 for a in rotated_news if a.get("link") not in sent_news_history)
        print(f"[INFO] Rotation Engine: Unified sort with {fresh_count} fresh articles available.")

        macro_intel_rows = ""
        earnings_intel_rows = ""
        semi_trade_rows = ""
        row_count = 0
        earn_count = 0
        semi_count = 0

        import re

        # V25.1: Keyword Saturation Limiter to prevent topic flooding (max 2 per topic)
        topic_counts = {
            "oil": 0,
            "energy": 0,
            "apple": 0,
            "tesla": 0,
            "fed": 0,
            "rate": 0,
            "rates": 0,
            "china": 0,
            "iran": 0,
            "israel": 0,
        }

        for i, res in enumerate(rotated_news):
            raw_title = res.get("title", "")
            cleaned_title = re.sub(r"\s+[-|•|–]\s+.*$", "", raw_title).strip()
            # V26.9: Purge lame 📊 emojis from headlines and replace with crisp »
            cleaned_title = cleaned_title.replace("📊", "»").strip()

            f_title = self.inject_price_flair(cleaned_title, prices, master_data)

            # V24.1: Separate Earnings Area Logic
            is_earn = (
                res.get("is_earnings")
                or "EARNINGS" in res.get("raw_title", "").upper()
                or res.get("source") == "CNBC Earnings"
            )

            added = False
            # V25.4: Build clean source label for display
            feed_name = res.get("source", "")
            display_src = res.get("display_source", feed_name)

            # V28: Deep Semi Intelligence logic (High Fidelity trade news)
            is_semi_trade = feed_name in semi_sources or res.get("is_semi", False)

            # V29.7.1: Cross-Categorization for Semi Integrity
            is_semi_topic = any(
                kw in f_title.upper()
                for kw in [
                    "NVIDIA",
                    "CHIP",
                    "SEMI",
                    "INTEL",
                    "AMD",
                    "TSMC",
                    "ASML",
                    "ARM",
                    "BROADCOM",
                ]
            )
            if is_semi_topic and not is_semi_trade and not is_earn:
                is_semi_trade = True  # Allow high-signal macro chips to fill semi slots

            if "Google News" in feed_name and display_src != feed_name:
                # Clean up common long publishers
                d_clean = display_src.replace("Investor's Business Daily", "IBD")
                d_clean = d_clean.replace("The Wall Street Journal", "WSJ")
                d_clean = d_clean.replace("Financial Times", "FT")
                d_clean = d_clean.replace("The Economic Times", "EconTimes")
                d_clean = d_clean.replace("The Motley Fool", "MotleyFool")
                d_clean = d_clean.replace("Barron's", "Barrons")
                src_label = d_clean
            else:
                src_label = display_src.replace("CNBC ", "").strip()

            # Truncate to keep badge tight
            if len(src_label) > 22:
                src_label = src_label[:22]

            # V26.9: Strip TLDs from source labels (AOL.COM -> AOL, BLOOMBERG.COM -> BLOOMBERG)
            src_label = re.sub(
                r"\.(COM|NET|ORG|CO|UK|IO|AI|INFO|EDU|GOV|US|BIZ|ME)$",
                "",
                src_label,
                flags=re.IGNORECASE,
            )

            # V28: Config-First source badge resolution (Case-Insensitive)
            space_map = getattr(agg, "SOURCE_SPACE_MAP", {})
            lookup_key = src_label.upper().replace(" ", "")
            if lookup_key in space_map:
                src_label = space_map[lookup_key]

            else:
                # Step 2: Auto-formatter reads rules from YAML auto_badge_rules via agg
                _acronym_max = getattr(agg, "BADGE_ACRONYM_MAX", 5)
                _camel_split = getattr(agg, "BADGE_CAMEL_SPLIT", True)

                def _fmt_badge(label, max_len=_acronym_max, do_split=_camel_split):
                    label = label.strip()
                    if " " in label:
                        return label.title()
                    if do_split:
                        split = re.sub(r"([a-z])([A-Z])", r"\1 \2", label)
                        if " " in split:
                            return split.title()
                    if len(label) <= max_len:
                        return label.upper()
                    return label.title()

                src_label = _fmt_badge(src_label)

            # monospaced badge
            SRC_BADGE = f'&nbsp;<span class="src-badge">[{src_label}]</span>'

            if is_semi_trade:
                if semi_count < 15:
                    row_class = "news-row-even" if semi_count % 2 == 0 else "news-row-odd"
                    semi_trade_rows += (
                        f'<div class="{row_class}" style="border-left:3px solid {gold};">'
                        f'<span style="font-size:14px; color:{gold};">★</span>&nbsp;'
                        f'<a href="{res["link"]}" class="news-link">'
                        f"{f_title}</a>{SRC_BADGE}</div>"
                    )
                    semi_count += 1
                    added = True

            elif is_earn:
                if earn_count < 8:
                    # V25.7: Institutional Blue Glassmorphism for Earnings
                    row_class = "earn-row-even" if earn_count % 2 == 0 else "earn-row-odd"
                    earnings_intel_rows += (
                        f'<div class="{row_class}">'
                        f'<span style="font-size:14px; color:#38bdf8;">◈</span>&nbsp;'
                        f'<a href="{res["link"]}" class="news-link">'
                        f"{f_title}</a>{SRC_BADGE}</div>"
                    )
                    earn_count += 1
                    added = True
            else:
                if row_count < 15:
                    # Check saturation for MACRO news
                    tl = res.get("title", "").lower()
                    score = res.get("final_score", res.get("score", 0))

                    # V27: Alpha Override - bypass saturation if score is high conviction
                    is_alpha = isinstance(score, (int, float)) and score > 120

                    is_saturated = False
                    matched_kws = []
                    for kw in topic_counts:
                        if re.search(r"\b" + kw + r"\b", tl):
                            if (
                                topic_counts[kw] >= 5
                            ):  # V29.7.1: Relaxed from 2 to 5 for hierarchy integrity
                                is_saturated = True
                            matched_kws.append(kw)

                    if is_saturated and not is_alpha:
                        print(f"[DEBUG] Skipped (Saturation) -> {res.get('title', 'Unknown')}")
                        continue

                    # Apply increments
                    for kw in matched_kws:
                        topic_counts[kw] += 1

                    row_class = "news-row-even" if row_count % 2 == 0 else "news-row-odd"
                    macro_intel_rows += (
                        f'<div class="{row_class}">'
                        f'<span style="font-size:14px;">&bull;</span>&nbsp;'
                        f'<a href="{res["link"]}" class="news-link">'
                        f"{f_title}</a>{SRC_BADGE}</div>"
                    )
                    row_count += 1
                    added = True

            if added:
                # V28: Unified Status Logic - Determine freshness before updating history
                is_new = res["link"] not in sent_news_history
                sent_news_history[res["link"]] = now_ts
                status = "FRESH" if is_new else "STALE"
                score = res.get("final_score", res.get("score", 0))
                if isinstance(score, float):
                    score = f"{score:.2f}"
                tag = "EARNINGS" if is_earn else ("SEMI" if is_semi_trade else "MACRO")
                print(
                    f"[DEBUG] Selected ({status}) [Score: {score}] -> [{tag}] {res.get('title', 'Unknown')}"
                )

            if row_count >= 15 and earn_count >= 8 and semi_count >= 15:
                # V28: Mandatory 15 SEMI articles cap
                if semi_count < 15 and i < (len(rotated_news) - 1):
                    continue
                print(
                    f"[INFO] News Quota Met: {row_count} Macro, {earn_count} Earnings, {semi_count} Semi (High-Fidelity)."
                )
                break

        # Save history for rotation
        try:
            sent_news_path.parent.mkdir(parents=True, exist_ok=True)
            with open(sent_news_path, "w", encoding="utf-8") as f:
                json.dump(sent_news_history, f)
        except Exception as e:
            print(f"[ERROR] Could not save sent news history: {e}")

        # V24.9: Reordered - Earnings Intelligence comes AFTER general news URLs
        if earnings_intel_rows:
            earnings_area = f'<div style="margin-top:20px; margin-bottom:20px;"><div class="section-hdr" style="color:{accent}; border-bottom:2px solid {accent}; display:inline-block; margin-bottom:12px; width:100%; text-align:center;">EARNINGS INTELLIGENCE</div>{earnings_intel_rows}</div>'
            macro_intel_rows = macro_intel_rows + earnings_area

        # Watchlist Intel Logic (V23.55)
        watchlist_intel_html = ""  # Minimal fallback for now to ensure recovery stability

        return (
            [],
            [],
            vibe_status,
            watchlist_intel_html,
            exec_summary,
            macro_intel_rows,
            semi_trade_rows,
        )

    def _render_valuation_row(self, item):
        """V28.8: Renders a high-density valuation row for the Intel Dashboard."""
        m_cap = item.get("market_cap")
        pe = item.get("pe")
        rev = item.get("rev")

    def _get_session_badge(self, s_type):
        s_type = (s_type or "CLOSED").upper()
        if s_type == "LIVE":
            return "L", "#10b981"
        if s_type in ["POST", "AH"]:
            return "AH", "#f59e0b"
        if s_type in ["PRE", "PM"]:
            return "PRE", "#f59e0b"
        if s_type == "OVN":
            return "OVN", "#f59e0b"
        return "C", "#f59e0b"

    def _render_valuation_row(self, item):
        m_cap = item.get("marketCap") or item.get("market_cap")
        pe = item.get("trailingPE") or item.get("trailing_pe")
        rev = item.get("revenueGrowth") or item.get("revenue_growth")
        if not any([m_cap, pe, rev]):
            return ""
        parts = []
        if m_cap:
            if m_cap >= 1e12:
                cap_str = f"${m_cap/1e12:.2f}T"
            elif m_cap >= 1e9:
                cap_str = f"${m_cap/1e9:.1f}B"
            else:
                cap_str = f"${m_cap/1e6:.1f}M"
            parts.append(f"Val: {cap_str}")
        if pe:
            parts.append(f"P/E: {pe:.1f}")
        if rev:
            parts.append(
                f"Rev: {rev*100:+.1f}%"
                if isinstance(rev, float) and rev < 10
                else f"Rev: ${rev/1e6:.1f}M"
            )
        content = " | ".join(parts)
        return f'<div class="vr">[ {content} ]</div>'

    def gather_all_data(self, custom_tickers=None, force=False):
        master = self._load_json("CPO_MASTER_DATA.json")
        prices_path = self.db_path / "live_prices.json"

        # V24.7: Direct Market Mover Intelligence (External Discovery)
        movers_ext = {"gainers": [], "losers": []}
        try:
            from market_movers_scraper import get_market_movers

            movers_ext = asyncio.run(get_market_movers())
            print(
                f"[INFO] [MOVERS] Discovered {len(movers_ext['gainers'])} gainers / {len(movers_ext['losers'])} losers."
            )
        except Exception as e:
            print(f"[WARN] Failed to scrape movers: {e}")
        prices_path = self.db_path / "live_prices.json"

        # V28: Price Freshness Governance
        # V23.88: Session Transition Intelligence
        # We refresh if:
        # 1. Prices are > 5 minutes old (Standard TTL)
        # 2. Market has transitioned sessions (e.g., PRE -> LIVE) since last fetch
        prices = {}
        if prices_path.exists():
            try:
                raw_prices = self._load_json("live_prices.json")
                # Detect session of the last fetch
                sample = next(iter([v for k, v in raw_prices.items() if k != "_meta"]), {})
                last_fetch_type = sample.get("ext_type", "UNKNOWN")
                current_sess = self.get_market_session()

                # Logic: If last was PRE and now is LIVE, or last was REG/LIVE and now is POST, force refresh.
                session_changed = (
                    (last_fetch_type == "PRE" and current_sess == "LIVE")
                    or (last_fetch_type == "LIVE" and current_sess == "AH")
                    or (last_fetch_type == "UNKNOWN")
                )

                stale_time = (time.time() - prices_path.stat().st_mtime) > 1800

                if force or stale_time or session_changed:
                    reason = (
                        "FORCE"
                        if force
                        else (
                            "STALE"
                            if stale_time
                            else f"SESSION TRANSITION ({last_fetch_type} -> {current_sess})"
                        )
                    )
                    print(f"[INFO] [CACHE] Refresh Triggered: {reason}. Hardening live data...")
                    try:
                        from live_prices import async_run_fetch

                        movers_list = movers_ext["gainers"] + movers_ext["losers"]
                        # V24.9: Explicitly include indices, global markets, and crypto to prevent 0.00% Pulse errors
                        pulse_anchors = [
                            "^GSPC",
                            "^IXIC",
                            "^DJI",
                            "ES=F",
                            "NQ=F",
                            "YM=F",
                            "BTC-USD",
                            "ETH-USD",
                            "SOL-USD",
                            "^HSI",
                            "^N225",
                            "^GDAXI",
                            "^FTSE",
                        ]
                        all_to_fetch = list(
                            set(master.keys())
                            | set([t.upper() for t in (custom_tickers or [])])
                            | set(movers_list)
                            | set(pulse_anchors)
                        )
                        # V26.9: Respect 15m Cache Mandate (Remove force=True)
                        prices = asyncio.run(
                            async_run_fetch(tickers=all_to_fetch[:250], skip_sync=True, force=force)
                        )
                        print(f"[INFO] [LIVE] JIT Refresh Complete: {len(prices)} tickers.")
                    except Exception as e:
                        print(f"[WARN] Price refresh failed: {e}. Falling back to disk.")
                        prices = raw_prices
                else:
                    prices = raw_prices
                    print(
                        f"[INFO] [CACHE] Prices Fresh: {int(300 - (time.time() - prices_path.stat().st_mtime))}s / Session: {current_sess}"
                    )
            except Exception as e:
                print(f"[WARN] Cache analysis failed: {e}. Forcing fresh fetch.")
                prices = self._load_json("live_prices.json")
        else:
            print("[INFO] [CACHE] Cache file missing. Forcing fresh fetch.")
            try:
                from live_prices import async_run_fetch

                movers_list = movers_ext["gainers"] + movers_ext["losers"]
                pulse_anchors = [
                    "^GSPC",
                    "^IXIC",
                    "^DJI",
                    "ES=F",
                    "NQ=F",
                    "YM=F",
                    "BTC-USD",
                    "ETH-USD",
                    "SOL-USD",
                    "^HSI",
                    "^N225",
                    "^GDAXI",
                    "^FTSE",
                ]
                all_to_fetch = list(
                    set(master.keys())
                    | set([t.upper() for t in (custom_tickers or [])])
                    | set(movers_list)
                    | set(pulse_anchors)
                )
                prices = asyncio.run(
                    async_run_fetch(tickers=all_to_fetch[:250], skip_sync=True, force=True)
                )
                print(f"[INFO] [LIVE] Initial Fetch Complete: {len(prices)} tickers.")
            except Exception as e:
                print(f"[WARN] Initial price fetch failed: {e}.")
                prices = {}

        news_db = self._load_json("YAHOO_NEWS_DB.json").get("news", {})
        sentiment = self.fetch_sentiment()

        print(
            f"[INFO] Analyzing Coverage: {len(master)} Master Tickers // {len(custom_tickers or [])} Custom Overrides."
        )

        tradeable = {"semi": [], "ai": [], "watchlist": []}
        strategic = []
        custom_set = set([t.upper() for t in custom_tickers]) if custom_tickers else set()

        for sym in set(master.keys()) | custom_set:
            res = master.get(sym, {}).get("human_research", {})
            p_data = prices.get(sym, {})
            _, pct, _ = self.get_session_data(p_data, sym)
            item = {
                "symbol": sym,
                "name": res.get("Company") or sym,
                "pct": pct or 0,
                "notes": res.get("Notes", ""),
                "alpha": float(res.get("Alpha Score", 0) or 0),
                "market_cap": p_data.get("market_cap"),
                "pe": p_data.get("pe"),
                "rev": p_data.get("rev"),
            }

            if sym in custom_set:
                tradeable["watchlist"].append(item)
            elif "semi" in (res.get("Role") or "").lower():
                tradeable["semi"].append(item)
            else:
                tradeable["ai"].append(item)

        for k in tradeable:
            tradeable[k].sort(key=lambda x: x["pct"], reverse=True)
        return tradeable, strategic, prices, news_db, sentiment, master, movers_ext

    def compose_html(
        self, tradeable, strategic, prices, news_db, sentiment, master, movers_ext=None
    ):
        # Design Tokens — matched to main site (#020617 deep navy base)
        bg_main = "#020617"  # site --bg-main
        bg_surface = "#0f172a"  # site --bg-card
        bg_accent = "#1e293b"  # site card inner / border layer
        bg_deep = "#0a0f1e"  # mid-layer (F&G boxes)
        text_dim = "#8f9bb3"
        text_bright = "#f8fafc"
        bull = "#10b981"  # green — matches site var(--green)
        bear = "#f43f5e"  # red   — matches site var(--danger)
        accent = "#6366f1"  # indigo — close to site var(--accent)
        gold = "#f59e0b"  # amber — site var(--gold)
        border = "#1e293b"  # site border line

        # V28: Dynamic Session detection for Global Header
        sess_now = self.get_market_session()
        session = (
            "WEEKEND INTEL"
            if self.now.weekday() >= 5 and not sess_now
            else f"MARKET {sess_now}"
            if sess_now
            else "MARKET CLOSED"
        )

        # Sentiment Calculations
        market_fg = int(sentiment.get("market", {}).get("value", 50))
        crypto_fg = int(sentiment.get("crypto", {}).get("value", 50))

        def get_fg_color(v):
            if v <= 25:
                return bear  # Extreme Fear
            if v <= 45:
                return "#ff9f1c"  # Fear
            if v <= 55:
                return text_dim  # Neutral
            if v <= 75:
                return bull  # Greed
            return "#6ee7b7"  # Extreme Greed (site green-300)

        fg_color_total = get_fg_color(market_fg)
        fg_color_crypto = get_fg_color(crypto_fg)

        def get_diff_str(price, pct, clr, fs="8px"):
            if not price or pct is None:
                return ""
            prev = price / (1 + pct / 100)
            diff = price - prev
            sign = "+" if diff >= 0 else ""
            return f'<div class="pulse-diff" style="font-size:{fs}; color:{clr}; opacity:0.8; font-weight:bold; margin-top:1px;">{sign}{diff:,.0f} pts</div>'

        def render_tile(symbol, name, val, pct, sess, color, width="33.33%"):
            tag_style = "text-decoration:none;"
            if sess in ("PRE", "AH", "POST"):
                tag_style = "text-decoration:underline;"
            val_str = f"{val:,.0f}" if val > 1000 else f"{val:.2f}"

            chg_bg = "rgba(16,185,129,0.08)" if pct >= 0 else "rgba(244,63,94,0.08)"
            arrow = "▲" if pct >= 0 else "▼"

            badge_html = self.get_session_tag_html(fs="10px", sess_override=sess)
            badge_div = (
                f'<div class="pulse-badge" style="margin-bottom:4px;">{badge_html}</div>'
                if badge_html
                else ""
            )

            return (
                f'<td width="{width}" style="padding:3px; vertical-align:top;">'
                f'<div class="pulse-tile">'
                f"{badge_div}"
                f'<div class="pulse-idx-name" style="{tag_style}">{name}</div>'
                f'<div class="pulse-val">{val_str}</div>'
                f'<div class="pulse-chg-box" style="background:{chg_bg}; color:{color};">'
                f"{arrow}{abs(pct):.1f}%"
                f'{get_diff_str(val, pct, color, fs="9px")}'
                f"</div></div></td>"
            )

        COMPARATIVE_INDICES = [
            {"name": "S&P 500", "cash": "^GSPC", "fut": "ES=F"},
            {"name": "NASDAQ", "cash": "^IXIC", "fut": "NQ=F"},
            {"name": "DOW 30", "cash": "^DJI", "fut": "YM=F"},
        ]

        is_live_main = self.get_market_session() in ("LIVE", "AH")
        is_futures_active = (self.now.weekday() == 6 and self.now.hour >= 18) or (
            self.now.weekday() < 5
        )

        def get_index_tiles(width="33.33%"):
            tiles = ""
            for index in COMPARATIVE_INDICES:
                target_ticker = index["cash"] if is_live_main else index["fut"]
                c_data = prices.get(target_ticker, {})
                c_val, c_chg, c_sess = self.get_session_data(c_data, target_ticker)
                if not is_live_main and not is_futures_active:
                    c_data = prices.get(index["cash"], {})
                    c_val, c_chg, _ = self.get_session_data(c_data, index["cash"])
                    c_sess = "CLOSED"
                c_color = bull if (c_chg or 0) >= 0 else bear
                label = "LIVE" if is_live_main else c_sess
                tiles += render_tile(
                    target_ticker,
                    index["name"],
                    c_val or 0,
                    c_chg or 0,
                    label,
                    c_color,
                    width=width,
                )
            return tiles

        crypto_tickers = ["BTC-USD", "ETH-USD", "SOL-USD"]

        def get_crypto_tiles(width="33.33%"):
            tiles = ""
            for t in crypto_tickers:
                p = prices.get(t, {})
                val, chg, sess = self.get_session_data(p, t)
                color = bull if chg >= 0 else bear
                tiles += render_tile(t, t.split("-")[0], val, chg, sess, color, width=width)
            return tiles

        def render_fg_tile(label, val, color, sub, width="50%"):
            return (
                f'<td style="width:{width}; padding:3px; vertical-align:top;">'
                f'<div style="background:#0a0f1e; border-radius:5px; padding:12px 8px; text-align:center;">'
                f'<div class="fg-label" style="font-size:8px; font-family:monospace; color:#8f9bb3; letter-spacing:1px; margin-bottom:3px;">{label}</div>'
                f'<div class="fg-val" style="font-size:32px; font-weight:900; color:{color}; line-height:1;">{val}</div>'
                f'<div style="font-size:7px; color:#8f9bb3; margin-top:2px;">{sub}</div>'
                f"</div></td>"
            )

        global_map = [
            ("HSI", "^HSI"),
            ("NIKKEI", "^N225"),
            ("DAX", "^GDAXI"),
            ("FTSE", "^FTSE"),
        ]

        def get_global_tiles(width_list):
            tiles = []
            hr = self.now.hour
            for i, (name, ticker) in enumerate(global_map):
                p = prices.get(ticker, {})
                val, chg, sess = self.get_session_data(p, ticker)
                color = bull if chg >= 0 else bear
                arrow = "▲" if chg >= 0 else "▼"
                is_open = (ticker in ("^HSI", "^N225") and (hr >= 20 or hr <= 4)) or (
                    ticker in ("^GDAXI", "^FTSE") and (3 <= hr <= 11)
                )
                badge = self.get_session_tag_html(
                    fs="10px", sess_override="LIVE" if is_open else "CLOSED"
                )
                chg_bg = "rgba(16,185,129,0.08)" if chg >= 0 else "rgba(244,63,94,0.08)"

                w = width_list[i] if i < len(width_list) else width_list[0]
                val_str = f"{val:,.0f}" if val else "0"
                inner = (
                    f'<div style="background:{bg_accent}; border-radius:5px; padding:12px 10px; text-align:center;">'
                    f'<div class="global-badge" style="margin-bottom:4px;">{badge}</div>'
                    f'<div class="global-label" style="font-family:sans-serif; color:{text_dim}; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">{name}</div>'
                    f'<div class="global-val" style="color:{text_bright}; font-size:16px; font-weight:bold; margin-bottom:2px;">{val_str}</div>'
                    f'<div class="global-chg" style="background:{chg_bg}; border-radius:3px; padding:4px 0; font-family:monospace; color:{color}; font-size:15px; font-weight:bold;">'
                    f"{arrow}{abs(chg):.1f}%"
                    f'<div style="font-size:9px; opacity:0.8; margin-top:2px;">{get_diff_str(p.get("price",0), chg, color, fs="9px")}</div>'
                    f"</div></div>"
                )
                tiles.append(
                    f'<td class="global-col" style="width:{w}; padding:3px; vertical-align:top;">{inner}</td>'
                )
            return tiles

        gainers_top = []
        losers_top = []

        if movers_ext:
            for sym in movers_ext.get("gainers", []):
                p_data = prices.get(sym, {})
                price, pct, sess = self.get_session_data(p_data, sym)
                if price:
                    gainers_top.append(
                        {
                            "symbol": sym,
                            "price": price,
                            "change_pct": pct,
                            "session": sess,
                        }
                    )

            for sym in movers_ext.get("losers", []):
                p_data = prices.get(sym, {})
                price, pct, sess = self.get_session_data(p_data, sym)
                if price:
                    losers_top.append(
                        {
                            "symbol": sym,
                            "price": price,
                            "change_pct": pct,
                            "session": sess,
                        }
                    )

        # Fallback to internal if external fails
        if not gainers_top and not losers_top:
            perf_candidates = []
            now_ts = time.time()
            for sym, p_data in prices.items():
                if sym == "_meta" or not self.is_legit_ticker(sym):
                    continue
                last_ts = p_data.get("timestamp", 0)
                if (now_ts - last_ts) > 21600:
                    continue
                price, pct, sess = self.get_session_data(p_data, sym)
                if pct is not None and abs(pct) > 0.05:
                    perf_candidates.append(
                        {
                            "symbol": sym,
                            "price": price,
                            "change_pct": pct,
                            "session": sess,
                        }
                    )
            gainers_top = sorted(
                [p for p in perf_candidates if p["change_pct"] > 0],
                key=lambda x: x["change_pct"],
                reverse=True,
            )[:10]
            losers_top = sorted(
                [p for p in perf_candidates if p["change_pct"] < 0],
                key=lambda x: x["change_pct"],
            )[:10]
        else:
            gainers_top = gainers_top[:10]
            losers_top = losers_top[:10]

        def render_perf_list(movers, title, color):
            items_html = []
            for s in movers:
                sym = s["symbol"]
                p_entry = prices.get(sym, {})

                # V26.8: Decoupled Price Logic (Closing vs Extended)
                reg_price = p_entry.get("price", 0)
                reg_pct = p_entry.get("change_pct", 0)
                ext_price = p_entry.get("ext_price")
                ext_pct = p_entry.get("ext_pct")
                sess = p_entry.get("ext_type", "LIVE")

                # V28.8: Use Session-Aware Primary Price for Movers
                price, pct, sess = self.get_session_data(p_entry, sym)

                color_movers = bull if pct >= 0 else bear
                pct_str = f"{'+' if pct >= 0 else ''}{pct:.2f}%"
                price_str = f"${price:,.2f}" if price > 0 else ""

                label_text, label_color = self._get_session_badge(sess)
                session_key = f'<span style="color:{label_color}; font-weight:900; font-size:10px;">{label_text}</span>'

                anchor = ""
                if sess in ["PRE", "AH", "OVN", "POST", "PM"]:
                    c_p = p_entry.get("close_price") or p_entry.get("price")
                    if c_p:
                        anchor = f'<span style="font-size:10px; color:{text_dim}; font-weight:normal;"> | C: ${c_p:,.2f}</span>'

                # V28.8: Mirrored Bucket Layout for Movers
                symbol_link = f'<a href="https://finance.yahoo.com/quote/{sym}" style="color:#f59e0b; text-decoration:none;">${sym}</a>'
                val_row = self._render_valuation_row(p_entry)

                price_html = f'<span style="color:#cbd5e1; font-size:13px; margin-right:6px;">{price_str}</span>'
                pct_display = f'{price_html}<span style="color:{color_movers}; font-weight:bold; font-size:14px;">{session_key} {pct_str}{anchor}</span>'

                items_html.append(
                    f"""
                    <div class="bi" style="border-left:3px solid {color_movers}; margin-bottom:6px; text-align:left;">
                        <table class="ut"><tr>
                            <td class="stc" style="font-size:16px;">{symbol_link}</td>
                            <td class="spc">{pct_display}</td>
                        </tr></table>
                        {val_row}
                    </div>"""
                )

            return f"""
                <div class="perf-cell" style="width:100%; text-align:center; margin-bottom:15px;">
                    <div class="perf-hdr" style="color:{color}; font-size:12px; font-weight:900; margin-bottom:10px; text-transform:uppercase; letter-spacing:1px;">{title}</div>
                    {''.join(items_html)}
                </div>
            """

        # 2c. Global Markets
        g_tiles = get_global_tiles(["25%", "25%", "25%", "25%"])
        global_grid_html = f'<tr>{"".join(g_tiles)}</tr>'

        # Build Unified Pulse Block
        unified_pulse = f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px;"><tr>{get_index_tiles("33.33%")}</tr></table>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px;"><tr>{get_crypto_tiles("33.33%")}</tr></table>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px;"><tr>
                {render_fg_tile("MARKET F&G", market_fg, fg_color_total, "FEAR & GREED", "50%")}
                {render_fg_tile("CRYPTO F&G", crypto_fg, fg_color_crypto, "COIN GLASS", "50%")}
            </tr></table>
            <div class="section-hdr" style="text-align:center;">GLOBAL MARKETS</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;">
                {global_grid_html}
            </table>
            <div class="section-hdr" style="text-align:center; color:{text_bright};">SESSION PERFORMANCE</div>
            <table width="100%" cellpadding="0" cellspacing="0"><tr>
                <td class="mover-col" width="50%" style="vertical-align:top; padding-right:5px;">
                    <div class="perf-hdr" style="font-size:16px; color:{bull}; font-weight:900; text-align:center; padding-bottom:12px; text-transform:uppercase; letter-spacing:2px;">▲ Top Gainers</div>
                    {render_perf_list(gainers_top, "", bull)}
                </td>
                <td class="mover-col" width="50%" style="vertical-align:top; padding-left:5px; padding-top:0;">
                    <div class="perf-hdr" style="font-size:16px; color:{bear}; font-weight:900; text-align:center; padding-bottom:12px; text-transform:uppercase; letter-spacing:2px;">▼ Top Losers</div>
                    {render_perf_list(losers_top, "", bear)}
                </td>
            </tr></table>
        """

        # 3. Narrative Intelligence
        (
            macro_ps,
            sector_ps,
            sentiment_label,
            watchlist_intel_html,
            exec_summary,
            macro_intel_rows,
            semi_trade_rows,
        ) = self.synthesize_dossier(news_db, prices, master, sentiment)
        macro_html = "".join(
            [
                f'<div style="color:{text_dim}; font-size:15px; line-height:1.7; margin-bottom:14px; white-space:normal !important; overflow:visible !important;">'
                f"{p}</div>"
                for p in macro_ps
            ]
        )

        def render_bucket(title, items, hide_notes=False, columns=1):
            if not items:
                return ""
            rows = []
            for t in items:
                sym = t.get("symbol", "").replace("$", "")
                p_entry = prices.get(t["symbol"], {})
                price, pct, sess = self.get_session_data(p_entry, t["symbol"])
                has_price = price and price > 0

                if not has_price:
                    pct_display = '<span style="color:#4a5568; font-size:9px;">N/A</span>'
                    clr = text_dim
                else:
                    clr = bull if pct >= 0 else bear

                    # V28.8: Dynamic Session Badge (L, AH, PRE, OVN, C)
                    label_text, label_color = self._get_session_badge(sess)
                    session_key = (
                        f'<span style="color:{label_color}; font-weight:900;">{label_text}</span>'
                    )

                    anchor = ""
                    if sess in ["PRE", "AH", "OVN", "POST"]:
                        c_p = p_entry.get("close_price") or p_entry.get("price")
                        if c_p:
                            anchor = f'<span style="font-size:10px; color:{text_dim}; font-weight:normal;"> | C: ${c_p:,.2f}</span>'

                    price_str = f'<span style="color:#cbd5e1; font-size:13px; margin-right:6px;">${price:,.2f}</span>'
                    pct_display = f'{price_str}<span style="color:{clr}; font-weight:bold; font-size:14px;">{session_key} {pct:+.2f}%{anchor}</span>'

                notes = "" if hide_notes else t.get("notes", "").strip()
                flaired_notes = self.inject_price_flair(notes, prices, link=False)
                display_name = (
                    t["name"]
                    if t["name"].upper() != sym.upper()
                    else self.ticker_name_map.get(sym, "")
                )

                rows.append(
                    f"""
                    <div class="bi" style="border-left:3px solid {clr};">
                        <table class="ut"><tr>
                            <td class="stc"><a href="https://finance.yahoo.com/quote/{t['symbol']}" style="color:{gold}; text-decoration:none;">${sym}</a></td>
                            <td class="spc">{pct_display}</td>
                        </tr></table>
                        {f'<div class="bn">{flaired_notes}</div>' if flaired_notes else ''}
                        {self._render_valuation_row(t)}
                    </div>"""
                )

            # If 2 cols, shard the rows
            if columns == 2:
                half = (len(rows) + 1) // 2
                col1 = "".join(rows[:half])
                col2 = "".join(rows[half:])
                content = f'<table width="100%" cellpadding="0" cellspacing="0"><tr><td class="bucket-col" width="50%" style="vertical-align:top; padding-right:4px;">{col1}</td><td class="bucket-col" width="50%" style="vertical-align:top; padding-left:4px;">{col2}</td></tr></table>'
            else:
                content = "".join(rows)

            return (
                f'<div style="margin-top:10px;">'
                f'<div class="section-hdr">{title}</div>'
                f"{content}</div>"
            )

        watchlist_html = render_bucket(
            "REAL-TIME WATCHLIST",
            tradeable.get("watchlist", []),
            hide_notes=True,
            columns=2,
        )
        # Merge Semi and AI, then sort by highest momentum to ensure dynamic rotation
        merged_intel = tradeable.get("semi", []) + tradeable.get("ai", [])
        merged_intel = sorted(merged_intel, key=lambda x: x.get("pct", 0), reverse=True)[:25]
        intelligence_html = render_bucket("TICKER DASHBOARD", merged_intel, columns=1)

        # Master Template Assembly — Responsive Single-Surface Design
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Base & Layout */
                body {{ margin:0; padding:0; background-color:{bg_main}; font-family:sans-serif; }}
                table {{ border-collapse:collapse; border-spacing:0; border:0; }}
                .wrap {{
                    background: #0f172a;
                    background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
                    padding:20px 16px;
                }}
                .main-table {{ max-width:600px; width:100%; margin:0 auto; }}

                /* Typography & Headers */
                .section-hdr {{
                    font-size:20px;
                    font-family:monospace;
                    color:{gold};
                    letter-spacing:4px;
                    text-transform:uppercase;
                    font-weight:900;
                    margin-top:25px;
                    margin-bottom:12px;
                    padding-bottom:8px;
                    border-bottom:1px solid rgba(245,158,11,0.3);
                    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
                }}
                .news-link {{ text-decoration:none !important; font-size:14px; font-weight:600; color:inherit !important; }}
                /* V28.8: Restored Source Badge Typography (Sans-Serif High Fidelity) */
                .src-badge {{ color:#f97316; font-size:10px; font-weight:900; letter-spacing:0.5px; text-transform:uppercase; vertical-align:middle; opacity:0.8; }}
                .earn-hdr {{ color:#f59e0b; font-size:18px; font-weight:900; margin-bottom:8px; text-transform:uppercase; letter-spacing:2px; }}

                /* Pulse Grid Components */
                .pulse-tile {{ background:{bg_deep}; border-radius:5px; padding:12px 10px; text-align:center; }}
                .pulse-idx-name {{ color:{text_dim}; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }}
                .pulse-val {{ color:{text_bright}; font-size:16px; font-weight:bold; margin-bottom:2px; }}
                .pulse-chg-box {{ border-radius:3px; padding:4px 0; font-family:monospace; font-size:15px; font-weight:bold; }}
                .pulse-diff {{ font-size:9px; opacity:0.8; font-weight:bold; margin-top:2px; }}

                /* Performance Movers */
                .perf-item-wrap {{ margin-bottom:4px; text-align:center; width:100%; }}
                .perf-item {{ display:block; width:100%; box-sizing:border-box; background:rgba(255,255,255,0.02); padding:8px 10px; border-radius:3px; font-family:monospace; font-size:15px; text-align:left; overflow:hidden; }}
                .perf-sym {{ font-weight:bold; min-width:50px; display:inline-block; }}
                .perf-sym a {{ color:#f59e0b; text-decoration:none; font-weight:bold; }}
                .perf-price {{ color:#cbd5e1; font-size:12px; opacity:0.8; }}
                .perf-pct {{ font-weight:900; font-size:15px; }}
                .u-nowrap {{ white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis; }}

                /* Watchlist & Intelligence (Minified Classes) */
                .bi {{ background:rgba(255,255,255,0.03); padding:5px 12px; border-radius:4px; margin-bottom:4px; }}
                .stc {{ font-family:monospace; font-weight:bold; font-size:18px; }}
                .spc {{ text-align:right; font-family:monospace; }}
                .bn {{ font-size:12px; color:#8f9bb3; margin-top:6px; line-height:1.6; overflow:hidden; max-height:80px; }}
                .vr {{ text-align:left !important; font-size:10px; color:#38bdf8; font-family:monospace; margin-top:0px; }}
                .ut {{ width:100% !important; border-collapse:collapse; }}

                /* News Alternates (V28: Institutional Dark Theme) */
                .news-row-even, .news-row-odd {{
                    padding:10px 14px;
                    margin-bottom:6px;
                    border-radius:4px;
                    border-left:3px solid rgba(255,255,255,0.1);
                    color:#f8fafc !important;
                }}
                .news-row-even {{
                    background:rgba(30,41,59,0.4);
                    border-bottom:1px solid rgba(255,255,255,0.03);
                }}
                .news-row-odd {{
                    background:rgba(15,23,42,0.6);
                    border-bottom:1px solid rgba(255,255,255,0.05);
                    border-left:3px solid {accent};
                }}
                .earn-row-even, .earn-row-odd {{ padding:6px 8px; margin-bottom:4px; border-radius:6px; background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); color:#64748b; font-weight:600; }}
                .earn-row-odd {{ background:rgba(255,255,255,0.03); color:#8f9bb3; }}

                /* Session Badges */
                .sess-badge {{ padding:1px 3px; border-radius:3px; font-weight:bold; margin-left:4px; border:1px solid rgba(255,255,255,0.05); vertical-align:middle; display:inline-block; }}
                .sess-live  {{ color:#10b981; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.2); vertical-align:baseline; }}
                .sess-pre, .sess-ovn {{ color:#f59e0b; background:rgba(245,158,11,0.1); }}
                .sess-ah    {{ color:#ef4444; background:rgba(239,68,68,0.1); }}
                .sess-closed {{ color:#94a3b8; background:rgba(148,163,184,0.1); }}

                /* V29.7.1: Mobile Header Refinement (30% Reduction & Center) */
                @media only screen and (max-width:599px) {{
                    .wrap {{ padding:8px !important; }}
                    .header-cell {{ text-align:center !important; }}
                    .hdr-title {{
                        font-size:24px !important;
                        text-align:center !important;
                        width: 100% !important;
                        display: block !important;
                    }}
                    .hdr-sub {{ text-align:center !important; }}
                    .global-col {{ display:inline-block !important; width:50% !important; box-sizing:border-box !important; margin:0 !important; }}
                    .mover-col {{ display:block !important; width:100% !important; padding-left:0 !important; padding-right:0 !important; padding-top:15px !important; }}
                    .pulse-idx-name {{ font-size:12px !important; margin-bottom:4px !important; }}
                    .pulse-val {{ font-size:20px !important; font-weight:900 !important; }}
                    .pulse-chg-box {{ font-size:14px !important; }}

                    .section-hdr {{
                        font-size:14px !important;
                        font-weight:900 !important;
                        letter-spacing:2px !important;
                        text-align:center !important;
                        border-bottom: 1px solid rgba(245,158,11,0.2) !important;
                    }}
                    .perf-hdr {{ font-size:14px !important; text-align:center !important; }}
                    .earn-hdr {{ font-size:14px !important; text-align:center !important; }}
                    .summary-hdr {{ font-size:14px !important; text-align:center !important; }}

                    .perf-item {{ padding:10px !important; }}
                    .bucket-col {{ display:block !important; width:100% !important; padding:0 !important; }}
                }}

                /* Desktop Density */
                @media only screen and (min-width:600px) {{
                    .main-table {{ max-width:850px !important; }}
                    .section-hdr {{
                        font-size:18px !important;
                        font-weight:900 !important;
                        letter-spacing:5px !important;
                        color:{gold} !important;
                        padding-bottom:10px !important;
                    }}
                    .pulse-idx-name {{ font-size:19px !important; letter-spacing:1.5px !important; margin-bottom:8px !important; }}
                    .pulse-val {{ font-size:22px !important; }}
                    .pulse-chg-box {{ font-size:29px !important; padding:4px 0 !important; }}
                    .pulse-diff {{ font-size:14px !important; margin-top:2px !important; }}
                    .fg-val {{ font-size:38px !important; }}
                    .fg-label {{ font-size:16px !important; }}
                    .sec-ticker {{ font-size:18px !important; }}
                    .sec-name {{ font-size:16px !important; }}
                    .sec-pct {{ font-size:18px !important; }}
                    .sec-notes {{ font-size:13px !important; line-height:1.6 !important; color:#8f9bb3 !important; }}
                    .sec-price {{ font-size:15px !important; font-weight:bold !important; color:{text_bright} !important; }}
                    .perf-item {{ font-size:18px !important; margin-bottom:6px !important; }}
                    .perf-hdr {{ font-size:18px !important; margin-bottom:15px !important; letter-spacing:3px !important; }}
                    .perf-cell {{ padding:0 4px !important; }}
                    .sector-card {{ padding:14px 18px !important; }}
                    .hdr-title {{ font-size:28px !important; }}
                    .hdr-sub {{ font-size:15px !important; }}
                }}
            </style>
        </head>
        <body>
        <div class="wrap">
        <center>
        <table class="main-table" border="0" cellspacing="0" cellpadding="0" style="text-align:left; font-family:'Helvetica Neue',Arial,sans-serif;">

            <!-- ═══ HEADER ═══ -->
            <tr><td style="padding-bottom:15px; border-bottom: 2px solid {accent};">
                <table width="100%" cellpadding="0" cellspacing="0"><tr>
                    <td class="header-cell">
                        <div class="header-title hdr-title" style="color:{text_bright}; font-size:42px; font-weight:900; letter-spacing:-1.5px; text-transform:uppercase; line-height:1.1;">Market Insights <span style="color:{accent};">and Intel</span></div>
                        <div style="color:{text_dim}; font-size:10px; font-family:monospace; margin-top:8px; letter-spacing:1px;">V28 // {self.now.strftime('%a %Y-%m-%d %H:%M EST')} // {session}</div>
                    </td>
                    <td class="badge-cell" style="text-align:right; white-space:nowrap; vertical-align:middle; padding-left:10px;">
                        <span style="background:{accent}; color:#fff; padding:4px 10px; font-size:9px; border-radius:2px; font-weight:bold; letter-spacing:1px;">CONFIDENCE: HIGH</span>
                    </td>
                </tr></table>
            </td></tr>

            <!-- ═══ PULSE BLOCK ═══ -->
            <tr><td class="narrative-box" style="background:{bg_surface}; padding:20px 0; border-radius:6px;">

                <div class="section-hdr">INDEX PULSE</div>

                <!-- Unified View Assembly -->
                {unified_pulse}

                <!-- Macro Intelligence leads the news flow -->
                <div style="margin-top:25px;">
                    <div class="section-hdr" style="display:inline-block; color:{accent}; border-bottom:2px solid {accent}; width:100%; text-align:center;">GLOBAL PULSE</div>
                    <div style="background:rgba(15,23,42,0.4); border:1px solid rgba(255,255,255,0.05); padding:18px; border-radius:4px; margin-bottom:20px; line-height:1.6;">
                        <div style="color:#f8fafc; font-size:15px; margin-bottom:15px;">{exec_summary}</div>
                        <div style="font-size:13px; font-family:monospace; color:{text_bright}; margin-top:10px;">
                            {macro_intel_rows}
                        </div>
                    </div>
                </div>

                <!-- DEEP SEMI INTELLIGENCE (V28 Trade News) -->
                {f'''<div style="margin-top:25px;">
                    <div class="section-hdr" style="display:inline-block; color:{gold}; border-bottom:2px solid {gold}; width:100%; text-align:center;">SEMI INSIGHT</div>
                    <div style="background:rgba(245,158,11,0.03); border:1px solid rgba(245,158,11,0.15); padding:15px; border-radius:4px; margin-bottom:20px;">
                        <div style="font-size:13px; font-family:monospace; color:{text_bright};">
                            {semi_trade_rows}
                        </div>
                    </div>
                </div>''' if semi_trade_rows else ''}

                <!-- WATCHLIST NEWS -->
                {watchlist_intel_html}
            </td></tr>

            <!-- Narrative Intel -->
            <tr><td style="padding-bottom:30px;">
                {watchlist_html}
                {intelligence_html}
            </td></tr>

            <!-- Footer -->
            <tr><td style="padding:30px 0; border-top:1px solid #25272d; text-align:center;">
                <div style="color:{text_dim}; font-size:10px; font-family:monospace;">
                    END OF DOSSIER // TRANSMISSION SECURE // {session}<br>
                    SOVEREIGN ENGINE HARDENED // AUTO-GENERATED BY GIGACPO V28
                </div>
            </td></tr>
        </table>
        </center>
        </body></html>
        """
        # V23.60: Gmail Clipping Defense (Minification)
        # Strips redundant spaces, tabs, and newlines between tags.
        minified = re.sub(r">\s+<", "><", html)
        minified = re.sub(r"<!--.*?-->", "", minified, flags=re.DOTALL)
        return minified

    def send_email(self, html, subject_override=None):
        u = os.getenv("GMAIL_USER")
        pk = os.getenv("GMAIL_APP_PASS")
        r = os.getenv("RECIPIENT_EMAIL", "rayjonesy@gmail.com")
        display_name = os.getenv("GMAIL_DISPLAY_NAME", "Market News")

        salt = uuid.uuid4().hex[:8]
        msg = MIMEMultipart()
        msg["From"] = f"{display_name} <{u}>"
        msg["To"] = r
        msg["Subject"] = (
            subject_override
            if subject_override
            else f"Market Insights and Sovereign Intel // {self.now.strftime('%m/%d/%y')} [{salt}]"
        )
        html_anti_clip = html.replace(
            "</body>",
            f'<div style="display:none; color:transparent; font-size:0px; height:0px;">Anti-clip UUID: {uuid.uuid4().hex} - Time: {datetime.datetime.now().isoformat()}</div></body>',
        )
        msg.attach(MIMEText(html_anti_clip, "html"))
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(u, pk)
                s.send_message(msg)
            print("[OK] DISPATCHED.")
            return True
        except Exception as e:
            print(f"[FAIL] {e}")
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GIGACPO Intelligence Dossier Engine")
    parser.add_argument("--test-email", action="store_true", help="Send a test email")
    parser.add_argument(
        "--force", action="store_true", help="Force fresh data fetch (bypass cache)"
    )
    parser.add_argument(
        "--sync-x", action="store_true", help="Synchronize X intelligence before run"
    )
    parser.add_argument("--tickers", type=str, help="Comma-separated list of custom tickers")
    args, unknown = parser.parse_known_args()

    custom_tickers = []
    if args.tickers:
        if args.tickers.endswith(".txt") and os.path.exists(args.tickers):
            with open(args.tickers, "r") as f:
                content = f.read()
                # Support newlines, spaces, and commas
                raw = content.replace("\n", ",").replace(" ", ",")
                custom_tickers.extend([t.strip().upper() for t in raw.split(",") if t.strip()])
        else:
            custom_tickers.extend([t.strip().upper() for t in args.tickers.split(",") if t.strip()])

    # Also support free-floating flags like --NVDA or trailing lists
    for u in unknown:
        if u.startswith("--") and len(u) > 2:
            t = u[2:].upper().replace(",", " ").split()[0]
            custom_tickers.append(t)
        elif not u.startswith("-"):
            for t in u.split(","):
                t = t.strip().upper()
                if t:
                    custom_tickers.append(t)

    # V23.48: Trigger Sparkline Sidecar Fetch (Async but isolated)
    try:
        try:
            from email_spark_fetcher import run_spark_fetch
        except ImportError:
            pass

        # Global 15m check before even hitting the sidecar
        spark_path = Path(__file__).parent.parent / "database" / "email_sparklines.json"
        stale_for_sidecar = []
        log.info("Skipping Email Sparkline Sidecar (Disabled)")
    except Exception as e:
        log.warning(f"Sparkline sidecar failed: {e}")

    def ts():
        return datetime.datetime.now().strftime("%H%M")

    print(f"[{ts()}] # V26.14: Sovereign Intelligence Engine — Temporal Hierarchy (EST)")
    engine = SovereignIntelligenceEngine()
    print(f"[{ts()}] [DEBUG] Engine initialized.")

    # V29.5: Paywall Intelligence Guardian (Daily Refresh)
    try:
        PaywallGuardian.check_for_updates(force=False)
    except Exception as e:
        print(f"[{ts()}] [WARN] [GUARDIAN] Intelligence sync skipped: {e}")

    if args.sync_x:
        print(f"[{ts()}] [SYNC] Triggering Social Intelligence Sync...")
        try:
            import subprocess

            subprocess.run([sys.executable, "engine/x_intel_instant_sync.py"], check=True)
        except Exception as e:
            print(f"[{ts()}] [ERROR] Social Sync Failed: {e}")

    # Filter custom tickers to legit ones
    print(f"[{ts()}] [DEBUG] Filtering custom tickers...")
    valid_custom = [t for t in custom_tickers if engine.is_legit_ticker(t)]
    if valid_custom:
        print(f"[{ts()}] [CLI] Custom Watchlist: {', '.join(valid_custom)}")

    print(f"[{ts()}] [DEBUG] Gathering all data...")
    tradeable, strategic, prices, news_db, sentiment, entries, movers_ext = engine.gather_all_data(
        custom_tickers=valid_custom, force=args.force
    )
    print(f"[{ts()}] [DEBUG] Data gathered. Composing HTML...")
    html = engine.compose_html(
        tradeable, strategic, prices, news_db, sentiment, entries, movers_ext=movers_ext
    )

    # Aggressive Minification for Gmail (102KB Limit)
    import re

    html = re.sub(r">\s+<", "><", html)
    html = re.sub(r"\s{2,}", " ", html)
    html = html.replace("\n", "").replace("\r", "")

    preview_path = engine.db_path / "synopsis_preview.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)

    payload_kb = len(html) / 1024
    print(f"Dossier generated: {preview_path}")
    print(
        f"Payload Size: {payload_kb:.1f} KB {'[OVER LIMIT - WILL CLIP]' if payload_kb > 102 else '[SAFE]'}"
    )

    # V28: Automatic Web Deployment (bmwseals.com/email)
    print(f"[{ts()}] [SYNC] Deploying to bmwseals.com/email...")
    RemoteSync.sync_file(preview_path)

    if args.test_email:
        import hashlib

        session_hash = hashlib.md5(html.encode()).hexdigest()[:8].upper()
        subject = (
            f"Market Insights and Intel // {engine.now.strftime('%Y-%m-%d')} // [{session_hash}]"
        )
        engine.send_email(html, subject_override=subject)

        # V28: Hardened Concise Logging Hierarchy
        # 1. Print Error Status first
        if error_monitor._MONITOR_INSTANCE:
            error_monitor._MONITOR_INSTANCE.print_summary()

        # 2. Print Intelligence Line
        print(f"[EMAIL] Intelligence: {subject}")

        # 3. Print Final Dispatch Confirmation
        dispatch_ts = (
            datetime.datetime.now().strftime("%a %b %d %I:%M:%S %p %Z %Y").replace("  ", " ")
        )
        print(f"Dispatched at {dispatch_ts}: SIE Pulse")
