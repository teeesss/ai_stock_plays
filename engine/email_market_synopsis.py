# V23.59: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
except ImportError:
    pass

import os
import json
import datetime
import smtplib
import re
import requests
import sys
import time
import argparse
import asyncio
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import uuid
import asyncio
import random
import re
import datetime
import calendar
import time
import math
from pathlib import Path
from curl_cffi import requests

# V23.59 Intelligence Foundation
try:
    from dependency_mgr import ensure_dependencies
    from live_prices import async_run_fetch
    from live_blog_scraper import LiveBlogScraper
    from local_nlp import LocalIntelligenceSynthesizer
    from macro_aggregator import MacroAggregator # V23.60 Aggregator
except ImportError:
    from engine.dependency_mgr import ensure_dependencies
    from engine.live_prices import async_run_fetch
    from engine.live_blog_scraper import LiveBlogScraper
    from engine.local_nlp import LocalIntelligenceSynthesizer
    from engine.macro_aggregator import MacroAggregator
    from engine.email_spark_fetcher import run_spark_fetch
from curl_cffi import requests as cffi_requests
import logging

# V23.47: Logger initialization
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)

load_dotenv()

class SovereignIntelligenceEngine:
    """
    GIGACPO SOVEREIGN INTELLIGENCE V4.3
    Aesthetics: Brand-Hardened (Blue/Gold/Green/Red)
    Logic: Global Macro Synthesis + Ticker Injection
    """
    def __init__(self):
        def ts(): return datetime.datetime.now().strftime("%H:%M:%S")

        print(f"[{ts()}] [DEBUG] Constructor: Setting paths...")
        self.root = Path(__file__).parent.parent
        self.db_path = self.root / "database"
        self.web_root = self.root / "web"
        
        # V23.58: Timezone-Aware Pulse
        # Normalizing to US/Eastern for consistent session tagging across VM/Server/Desktop
        self.now = self._get_est_now()
        
        # Design Tokens
        self.COLOR_BG = "#020617"; self.COLOR_CARD = "#0f172a"
        self.COLOR_LITE_BLUE = "#0ea5e9"; self.COLOR_GOLD = "#f59e0b"
        self.COLOR_GREEN = "#10b981"; self.COLOR_DANGER = "#f43f5e"
        self.COLOR_TEXT = "#f8fafc"; self.COLOR_DIM = "#64748b"
        
        # V22.7: Load massive symbol bridge
        print(f"[{ts()}] [DEBUG] Constructor: Loading ticker_name_map.json...")
        start = time.time()
        self.ticker_name_map = self._load_json("ticker_name_map.json")
        elapsed = time.time() - start
        print(f"[{ts()}] [DEBUG] Constructor: Map loaded ({len(self.ticker_name_map)} entries) in {elapsed:.2f}s.")

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
        "NVIDIA": "NVDA", "GOOGLE": "GOOGL", "ALPHABET": "GOOGL", "AMAZON": "AMZN",
        "APPLE": "AAPL", "MICROSOFT": "MSFT", "META": "META", "FACEBOOK": "META",
        "TESLA": "TSLA", "BROADCOM": "AVGO", "MARVELL": "MRVL", "TSMC": "TSM",
        "TAIWAN SEMI": "TSM", "ARM HOLDINGS": "ARM", "NOKIA": "NOK", "AMKOR": "AMKR",
        "NXP": "NXPI", "AXT": "AXTI", "CAMTEK": "CAMT", "SYNOPSYS": "SNPS",
        "MACOM": "MTSI", "VIAVI": "VIAV", "SIFIVE": "NVDA", "KLA": "KLAC",
        "J.P. MORGAN": "JPM", "CIBC": "CM", "ROYAL BANK": "RY", "RBC": "RY",
        "BMW": "BMWYY", "ASE": "ASX", "IPG": "IPGP", "ASMPT": "0522.HK",
        "GOOGLE": "GOOGL", "ALPHABET": "GOOGL", "MICROSOFT": "MSFT", "APPLE": "AAPL",
        "AMAZON": "AMZN", "TESLA": "TSLA", "META": "META", "NVIDIA": "NVDA"
    }

    def _load_aliases(self):
        """Merges manual high-fidelity aliases with the auto-generated 1,931-item brand bridge."""
        merged = self.ALIAS_MAP.copy()
        try:
            brand_bridge = self._load_json("name_aliases.json")
            merged.update(brand_bridge)
        except: pass
        return merged

    def is_legit_ticker(self, t):
        t = t.upper()
        if len(t) < 2 or t.isdigit(): return False
        # V22.10: Production Leak Suppression (Blacklisting common non-tradeable jargon)
        noise = {
            "AI", "ETF", "US", "EST", "MARKET", "NLP", "DOW", "NASDAQ", "FED", "CPI", "PPI", "GDP",
            "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CNY", "EPS", "ROE", "ROI", "PE", "YTD", "MTD",
            "CAGR", "MCAP", "APY", "APR", "SPX", "NDX", "RUT", "NQ", "ES", "YM",
            "Q1", "Q2", "Q3", "Q4", "FY26", "FY27", "IPO", "FDA", "SEC", "NASA", "HELOC", "SWOT", "ASIC",
            "NYSE", "AMEX", "CBOE", "LIQUIDITY", "VOLUME", "TOTAL", "HIGH", "LOW", "OPEN", "CLOSE",
            "AND", "FOR", "THE", "WITH", "FROM", "THIS", "THAT", "THEY", "HAVE", "SOME", "POS", "ITS",
            "TECH", "SENTIMENT", "POSITION", "ALPHA", "BETA", "GAMMA", "DELTA", "THETA", "VEGA",
            "CAPABILITIES", "RESEPI", "ACQUISITION", "ANNOUNCES", "ANNOUNCEMENT", "OFFERING",
            "VISUAL", "INSPECTION", "METROLOGY", "SUPER", "POWER", "GREEN", "BLUE", "RED", "OF", "TO",
            "IN", "OR", "IT", "IS", "AS", "BE", "AN", "SO", "ME", "ON", "AT", "BY", "IF", "NASA",
            "HLSE", "EMS", "OSAT", "ESA", "BLA", "ENXTAM", "DEEPEN", "JVCKENWOOD", "J.P", "RAN",
            "M1", "M2", "M3", "G1", "G3", "G5", "UX111", "PFIC", "EUV", "ITS", "AOI", "MKS", "G3", "G2",
            "CEO", "IRA", "NV", "SAVE", "LAYER", 
            "USDC", "USDT", "DAI", "BUSD", "PYUSD", "TUSD", "FDUSD", "FRAX", "LUSD", "USDD", "GUSD", "STETH", "WSTETH",
            "USDC-USD", "USDT-USD", "DAI-USD", "BUSD-USD", "PYUSD-USD", "TUSD-USD", "FDUSD-USD", "USDC.CX", "USDT.CX",
            "SK", "RAN", "DEEPEN", "SZKMY", "PT", "PTO"
        }
        if t in noise: return False
        if t.startswith("FY20") or t.startswith("P500"): return False
        return True

    def _load_json(self, name):
        p = self.db_path / name
        try:
            with open(p, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}

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
        except: return False

    def is_market_active(self):
        # V22.7: Expanded Market Session (Premarket/Afterhours/Futures)
        hr = self.now.hour; day = self.now.weekday()
        # Sunday Night Futures (6 PM EST+)
        if day == 6 and hr >= 18: return True
        # Saturday / Sunday Day (Stasis)
        if day >= 5: return False 
        # Weekday Window: Premarket (4 AM) thru Afterhours (8 PM)
        if 4 <= hr < 20: return True
        return False

    def is_entity_fresh(self, t, prices):
        """Global 15-minute TTL check (V22.7)"""
        existing = prices.get(t, {})
        if not existing or existing.get('price') is None: return False
        
        ts = existing.get('timestamp', 0)
        now = time.time()
        
        # V22.7: Strict 15-Minute Global TTL Bypass
        # If the market is active (Regular, Extended, or Futures) OR asset is Crypto -> 15m rule
        if self.is_market_active() or "USD" in t:
            return (now - ts) < 900 # 15 min check (Global)
            
        # Weekend / Middle-of-Night Stasis (Market Dead) -> Fresh from memory
        # This anchors Friday close prices til Sunday Night Futures open.
        return True

    def fetch_sentiment(self):
        market_val = 50; crypto_val = 50
        try:
            r = cffi_requests.get('https://feargreedmeter.com/', impersonate='chrome146', timeout=10)
            m = re.findall(r'<div[^>]*>(\d+)</div>', r.text)
            if m: market_val = int(m[0])
        except: pass
        try:
            r = cffi_requests.get('https://feargreedmeter.com/crypto', impersonate='chrome146', timeout=10)
            m = re.findall(r'<div[^>]*>(\d+)</div>', r.text)
            if m: crypto_val = int(m[0])
        except: pass

        def label(v):
            if v <= 25: return "EXTREME FEAR"
            if v <= 45: return "FEAR"
            if v <= 55: return "NEUTRAL"
            if v <= 75: return "GREED"
            return "EXTREME GREED"

        return {"market": {"value": market_val, "label": label(market_val)}, "crypto": {"value": crypto_val, "label": label(crypto_val)}}

    def is_legit_ticker(self, sym):
        if not sym or not isinstance(sym, str): return False
        sym = sym.upper()
        # V22.8: High-Fidelity Noise Shield
        # Filter company names or noise accidentally being treated as tickers
        if any(x in sym for x in [" ", "/", "\\", "(", ")", ".", ",", ":"]): return False
        if len(sym) < 1 or len(sym) > 12: return False
        
        # 1. Mandatory 2-Letter Whitelist (Filters out IN, OF, TO, BY, etc.)
        if len(sym) == 2:
            WHITELIST_2 = {
                "BA", "GM", "GE", "MU", "FN", "V", "MA", "T", "F", "KO", "VZ", "PYPL", 
                "UBER", "LYFT" # Some 4-char are fine, but 2-char are risky
            }
            # Only allow common 2-letter stocks or if they are in master_data
            return sym in WHITELIST_2
            
        # 2. Financial Acronym & Intelligence Blacklist
        # These are common high-signal words that are NOT tickers in news context
        FETCH_BLACKLIST = {
            "AI", "US", "NYSE", "NASDAQ", "ITS", "OSAT", "POS", "AND", "RESEPI", 
            "NASA", "EUV", "ESA", "PT", "PTO", "M1", "M2", "M3", "G1", "G2", "G3", "G5",
            "YTD", "HELOC", "APY", "APR", "PE", "EPS", "ROE", "ROIC", "EBITDA", "GAAP",
            "CFO", "COO", "CEO", "CTO", "IPO", "LBO", "PFIC", "FATCA", "ETF", "IRA", 
            "HSA", "RAN", "EMS", "LIDE", "HBM", "DRAM", "NAND", "CPO", "GPU", "CPU",
            "NPU", "LSA", "NLP", "AIAI", "S&P", "DJI", "SNP", "QQQ", "CD",
            # V22.99: Hardened Stablecoin Purge
            "USDC", "USDT", "DAI", "BUSD", "PYUSD", "TETHER", "STABLECOINS", "FDUSD"
        }
        if sym in FETCH_BLACKLIST: return False
        return True

    def is_shite_ticker(self, sym):
        """V23.01: Aggressive Stablecoin and Fake-Ticker Purge."""
        if not sym: return True
        t_up = sym.upper()
        # Stablecoin list
        if any(sc in t_up for sc in ["USDC", "USDT", "TETHER", "STABLECOIN", "DAI", "BUSD", "PYUSD", "CIRCLE", "FDUSD"]): return True
        # Generic noise
        if t_up in ["YAHOO", "BREAKING", "NEWS", "STOCK", "MARKET"]: return True
        return False

    def fetch_live_macro(self):
        # V22.96: Prioritized Multi-Stream News Engine (Triple-Feed V3.1)
        FEEDS = [
            ("https://finance.yahoo.com/rss/topic/analysis", 30),
            ("https://finance.yahoo.com/rss/topic/economic-news", 20),
            ("https://finance.yahoo.com/rss/topic/stock-market-news", 10)
        ]
        
        # Blacklist/Multipliers
        BLACKLIST = ["jim cramer", "mad money", "motley fool", "zacks", "investorplace", "simply wall st", "benzinga", "david einhorn"]
        # Tier 1 (+50): High-Impact Volatility/Geopolitics
        URGENT = ["war", "iran", "israel", "conflict", "missile", "strike", "emergency", "oil", "crude", "brent", "energy", "geopolitical"]
        # Tier 2 (+40): Macro Indicators
        MACRO = ["jobs report", "unemployment", "nfp", "payrolls", "cpi", "inflation", "fed", "powell", "rate hike", "rate cut"]
        # Tier 3 (+30): Corporate/Earning Highlights
        CORP = ["earnings", "beat", "miss", "eps", "revenue", "guidance", "buyback", "m&a", "acquisition"]

        headlines = []
        seen_urls = set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        # Load master keys for Ticker Match boost (+20)
        master_keys = set()
        try:
            m_data = self._load_json("CPO_MASTER_DATA.json")
            master_keys = set(m_data.keys())
        except: pass

        for url, base_score in FEEDS:
            try:
                # Stealth Jitter: Prevent 429 via staggered bursts
                time.sleep(random.uniform(1.2, 3.1))
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    print(f"[RSS WARN] {url} returned {r.status_code}")
                    continue

                items = re.findall(r'<item>(.*?)</item>', r.text, re.DOTALL)
                for item in items:
                    t_match = re.search(r'<title>(.*?)</title>', item)
                    l_match = re.search(r'<link>(.*?)</link>', item)
                    d_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                    
                    if t_match and l_match:
                        t = t_match.group(1).replace("&apos;", "'").replace("&quot;", '"').replace("<![CDATA[", "").replace("]]>", "")
                        l = l_match.group(1).replace("<![CDATA[", "").replace("]]>", "")
                        
                        # Dedup & Blacklist
                        if l in seen_urls: continue
                        t_lower = t.lower()
                        if any(b in t_lower for b in BLACKLIST): continue
                        
                        # SCORING (V3.1 Impact Matrix)
                        score = base_score
                        if any(k in t_lower for k in URGENT): score += 50
                        if any(k in t_lower for k in MACRO): score += 40
                        if any(k in t_lower for k in CORP): score += 30
                        
                        # Ticker Match (+20) - Fast set check
                        words = set(re.findall(r'\b[A-Z]{2,6}\b', t))
                        if words.intersection(master_keys): score += 20
                        
                        d = ""
                        if d_match:
                            d = d_match.group(1).replace("<![CDATA[", "").replace("]]>", "")
                            d = re.sub(r'<.*?>', '', d) # Strip HTML
                            d = re.sub(r'Read more on Yahoo Finance.*', '', d).strip()
                        
                        headlines.append({
                            'title': t, 
                            'link': l, 
                            'summary': d, 
                            'score': score
                        })
                        seen_urls.add(l)
            except Exception as e:
                print(f"[RSS ERR] {url}: {e}")

        # Top 15 Final Ranking
        headlines.sort(key=lambda x: x['score'], reverse=True)
        return headlines[:15]

    async def fetch_agg(self):
        """Aggregates and scores news with hardening/stealth protocols."""
        # V23.61: 15-minute Cache Enforcement
        pass

    async def fetch_priority_signals(self):
        """V23.55: Surgical harvest for high-alpha tech priority tickers/keywords."""
        ROOT = Path(__file__).parent.parent
        PATH = ROOT / "priority_tickers.txt"
        if not PATH.exists(): return []

        tickers = []
        with open(PATH, 'r') as f:
            for line in f:
                t = line.strip()
                if t: tickers.append(t)
        
        if not tickers: return []

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
                url = s.get('link') or s.get('url')
                if not url or url in seen_urls: continue
                
                title = s.get('title', '')
                # Base Priority Score
                score = 250 
                
                # Cross-Ticker Match Discovery (+100)
                # If target is MRVL, and title mentions GOOGL/GOOGLE
                t_lower = title.lower()
                matches = re.findall(r'\b[A-Z]{2,6}\b', title)
                if len(set(matches)) > 1: score += 100
                
                # Keyword Boost (+50)
                if any(k in t_lower for k in ["photonics", "cpo", "co-packaged", "interconnect", "chiplet"]):
                    score += 50
                
                priority_headlines.append({
                    'title': title,
                    'link': url,
                    'summary': s.get('summary', ''),
                    'score': score,
                    'is_priority': True,
                    'target': target
                })
                seen_urls.add(url)

        priority_headlines.sort(key=lambda x: x['score'], reverse=True)
        return priority_headlines[:10]

    def get_market_session(self, symbol=None, dt_override=None):
        # V22.93: Precise Session Detection + Overnight Awareness
        # V23.47: Suffix-Aware Global Exchange Logic
        # V23.90: Testable dt_override
        target_dt = dt_override if dt_override else self.now
        hr = target_dt.hour; mn = target_dt.minute
        tm = hr * 100 + mn
        day = target_dt.weekday()
        
        # 1. Crypto & Sunday Futures Override
        if symbol and symbol.endswith("-USD"): return "LIVE"
        if day == 6 and hr >= 18: return "OVN"
        if day >= 5: return "" # Weekend Stasis
        
        # 2. Exchange Hour Mapping (Normalization to EST)
        # Default: US (09:30 - 16:00)
        open_m, close_m = 930, 1600
        
        if symbol:
            s_up = symbol.upper()
            # Europe (DE/ST/L/PA/MI/MC/AS): ~03:00 - 11:30 EST
            if any(s_up.endswith(s) for s in [".DE", ".ST", ".L", ".PA", ".MI", ".MC", ".AS"]):
                open_m, close_m = 300, 1130 
            # Asia (HK/N225): ~21:30 - 04:00 EST
            elif any(s_up.endswith(s) for s in [".HK", ".N225", ".TW", ".KS"]):
                open_m, close_m = 2130, 400 # Spans midnight
            # Australia (AX/CX): ~19:00 - 01:00 EST
            elif any(s_up.endswith(s) for s in [".AX", ".CX"]):
                open_m, close_m = 1900, 100  # Spans midnight

        # 3. Session Classification
        is_live = False
        if open_m < close_m:
            is_live = (open_m <= tm < close_m)
        else: # Overnight markets (Asia/Australia)
            is_live = (tm >= open_m or tm < close_m)
            
        if is_live: return "LIVE"
        
        # US-Centric Extended Hours (V23.58 Labels: PRE/AH)
        if day < 5:
            # Morning Session: 4AM - 9:30AM EST
            if 400 <= tm < open_m: return "PRE"
            # Evening Session: 4PM - 8PM EST
            if close_m <= tm < 2000: return "AH"
            # Overnight / Late Night
            if tm >= 2000 or tm < 400: return "OVN"
        return ""

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
            match = (ext_type == sess)
            # Aliases for same session (POST == AH, PRE == PM/PRE)
            if not match:
                match = (sess == "AH" and ext_type in ["POST", "AH"]) or (sess == "PRE" and ext_type == "PRE")
            
            # V23.80: OVN Fallback — If we are in PRE (4AM-9:30AM) but only have OVN data, use OVN
            if not match and sess == "PRE" and ext_type == "OVN":
                match = True

            # V23.87: Atomic override to prevent mixed state ($REG + %EXT)
            # We only override if it's a confirmed session match OR if the data is explicitly LIVE
            if match or (sess == "LIVE" and ext_type == "LIVE"):
                e_p = p_data.get("ext_price")
                e_pct = p_data.get("ext_pct")
                
                # V24.4: If we have an extended price, use it, but calculate TOTAL change from previous close
                if e_p is not None:
                    price = e_p
                    prev = p_data.get("prev_close") or p_data.get("close_price")
                    if prev:
                        pct = ((price / prev) - 1) * 100
                    elif e_pct is not None:
                        pct = e_pct
                    
                    if match:
                        effective_sess = ext_type # Only override session string if we actually used ext data
        
        return price, pct, effective_sess

    def get_session_tag_html(self, fs="9px", color=None, sess_override=None):
        sess = sess_override if sess_override is not None else self.get_market_session()
        if not sess: return ""
        
        # V23.55: User-defined session colors
        # PRE = Orange, PM = Blue, AH = Red, OVN = Amber, LIVE = Green
        bg = "rgba(148,163,184,0.1)" # Default dim
        text_color = color if color else "#94a3b8"
        
        if sess == "PRE" or sess == "PM":
            text_color = "#f59e0b" # Orange
            bg = "rgba(245,158,11,0.1)"
            if sess == "PM": # Standardize
                sess = "PRE"
        elif sess == "AH" or sess == "POST":
            sess = "AH" # Standardize
            text_color = "#ef4444" # Red
            bg = "rgba(239,68,68,0.1)"
        elif sess == "OVN":
            text_color = "#f59e0b" # Amber
            bg = "rgba(245,158,11,0.1)"
        elif sess == "LIVE": 
            bg = "rgba(16,185,129,0.12)" # Green
            return f'<span class="sess-badge sess-live" style="font-size:{fs}; color:#10b981; background:{bg}; padding:1px 3px; border-radius:3px; font-weight:bold; margin-left:4px; vertical-align:baseline; border:1px solid rgba(16,185,129,0.2);">L<span style="color:#10b981;">⚡</span></span>'
        
        return f'<span class="sess-badge sess-{sess.lower()}" style="font-size:{fs}; color:{text_color}; background:{bg}; padding:1px 3px; border-radius:3px; font-weight:bold; margin-left:4px; vertical-align:middle; border:1px solid rgba(255,255,255,0.05);">{sess}</span>'

    def get_context_icon(self, title, used_icons=None):
        """V23.60: Context-aware icon selection with deep rotation and de-duplication."""
        t = title.lower()
        
        # Priority mapping: Keyword -> Icon Pool (Expanded for 100% variety)
        mapping = [
            (['war', 'iran', 'israel', 'conflict', 'missile', 'attack', 'strike', 'defense', 'military', '1930s', 'pentagon', 'strike'], ["🛡️", "⚔️", "🛰️", "🪖", "🎯", "⚓"]),
            (['oil', 'energy', 'fuel', 'shuttering', 'hormuz', 'crude', 'gas', 'gasoline', 'power grid', 'nuclear'], ["🛢️", "⚡", "🔥", "☢️", "🔌", "🌋"]),
            (['fed', 'rate', 'powell', 'inflation', 'cpi', 'jobs', 'yield', 'budget', 'debt', 'economy', 'recession', 'unemployment'], ["⚖️", "📉", "🏛️", "📋", "🏢", "🏘️", "🕰️"]),
            (['ai ', 'chip', 'nvidia', 'broadcom', 'semiconductor', 'mrvl', 'amd', 'quantum', 'robotics', 'hbm', 'foundry', 'gpu'], ["🧠", "🤖", "📟", "💾", "🔌", "⚙️", "🔬"]),
            (['earnings', 'revenue', 'quarterly', 'profit', 'dividend', 'guidance', 'record high', 'market today', 'stocks fall', 'stocks rise', 'shares leap', 'beat'], ["📈", "📊", "🎯", "💎", "💰", "🏆", "🌟"]),
            (['software', 'cloud', 'saas', 'meta', 'google', 'apple', 'amazon', 'tech', 'online', 'data center', 'network'], ["💻", "🌐", "☁️", "📱", "📡", "🖱️", "🖲️"]),
            (['lawsuit', 'sec', 'investigation', 'regulation', 'agenda', 'trump', 'administration', 'policy', 'doj', 'court'], ["📜", "🔨", "🗳️", "⚖️", "📢", "🖋️"]),
            (['bitcoin', 'crypto', 'btc', 'eth', 'sol', 'coinbase', 'aave', 'ledger', 'stablecoin', 'defi'], ["🪙", "🔗", "💎", "👾", "🕸️", "🗝️"]),
            (['scam', 'fake', 'gold', 'romance', 'pig-butchering', 'theft', 'stole', 'fraud', 'hacking', 'cyber'], ["🕵️", "🔐", "🚨", "🚫", "👺", "👤"]),
            (['millionaire', 'wealth', 'save', 'money', 'investing', 'math', 'portfolio', 'fund'], ["💰", "💵", "🏦", "💳", "🛒", "🛍️"]),
            (['export', 'truck', 'logistic', 'border', 'shipping', 'freight', 'supply chain', 'cargo'], ["🚛", "📦", "🚢", "🛫", "🚆", "⚓"]),
            (['photonics', 'cpo', 'fiber', 'laser', 'connectivity', 'optical', 'bandwidth'], ["📡", "✨", "📶", "⚡", "🌈", "📽️"])
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
            pool = ["📡", "🛰️", "🔭", "🔬", "🪐", "🌠", "🔮", "🧬", "🧪", "⚙️", "🛠️", "📡", "🛰️"]
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
        if symbol.startswith("$"): symbol = symbol[1:]
        p = prices.get(symbol)
        gold = self.COLOR_GOLD
        
        # Neutralize auto-linking for international symbols (LPK.DE -> LPK.&#8203;DE)
        display_sym = symbol
        if not link and "." in display_sym:
            display_sym = display_sym.replace(".", ".&#8203;")

        if not p or (p.get('price') is None and p.get('ext_price') is None): 
            style = f'color:{gold}; font-weight:bold; text-decoration:none;'
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
            if c_p: anchor = f'<span style="font-size:9px; color:#94a3b8; font-weight:normal;">&nbsp;| C: ${c_p:,.2f}</span>'

        style = f'color:{gold}; font-weight:bold; text-decoration:none;'
        pct_style = f'color:{color}; font-weight:800; text-decoration:none;'

        if simple:
            return f'<span style="{style}">{display_sym}</span>&nbsp;<span style="color:#cbd5e1; font-size:11px;">${price:.2f}</span>&nbsp;<span style="{pct_style}">{pct:+.2f}%{sess_tag}{anchor}</span>'
        return f'<span style="{style}">${display_sym}</span>&nbsp;<span style="color:#cbd5e1; font-size:12px;">${price:.2f}</span>&nbsp;<span style="{pct_style}">{emoji}&nbsp;{pct:+.2f}%{sess_tag}{anchor}</span>'

    def _fetch_ancillary_prices(self, tickers, prices):
        """V22.9: Hardened discovery hydration with 15m Global TTL bypass."""
        if not tickers: return {}
        # V22.54: Hardened remapping for common crypto/OTC aliases
        remapped = []
        for t in tickers:
            if not self.is_legit_ticker(t): continue
            
            # Map aliases
            final_t = t
            if t == "ADA": final_t = "ADA-USD"
            elif t == "BMWYY": final_t = "BMW.DE"
            
            # V22.9: STRICT 15M WAIT before discovery fetch
            if self.is_entity_fresh(final_t, prices):
                ts = prices.get(final_t, {}).get('timestamp', 0)
                age = int(time.time() - ts) // 60
                print(f"[CACHE] Discovery Fresh: {final_t} ({age}m old) - Skip fetch.")
                continue
                
            remapped.append(final_t)
            
        if not remapped: return {}
        try:
            print(f"[INTEL] discovery hydration required for {len(remapped)} assets...")
            new_prices = asyncio.run(async_run_fetch(tickers=remapped, dry_run=False, skip_sync=False))
            return new_prices
        except Exception as e:
            print(f"[ERR] Ancillary fetch failed: {e}")
            return {}

    def inject_price_flair(self, text, prices, master=None, link=True):
        """High-density utility to inject real-time price info into headlines."""
        if not text: return text
        words = text.split()
        for i, word in enumerate(words):
            clean_word = word.strip(".,;:()$").upper()
            if clean_word in prices:
                p_data = prices[clean_word]
                # V23.85: Force Session Awareness in headlines
                price, pct, sess = self.get_session_data(p_data, clean_word)
                if price is None or pct is None: continue
                
                color = "#22c55e" if pct >= 0 else "#ef4444"
                sign = "+" if pct >= 0 else ""
                sess_tag = self.get_session_tag_html(fs="8px", sess_override=sess)
                
                anchor = ""
                if sess in ["PRE", "AH", "OVN", "POST"]:
                    c_p = p_data.get("close_price") or p_data.get("price")
                    if c_p: anchor = f' <span style="font-size:8px; color:#94a3b8; font-weight:normal;">| C: ${c_p:,.2f}</span>'

                if f"(${price:.2f}" not in text:
                    flair = f'<strong>{word}</strong>&nbsp;(<span style="color:{color}; font-weight:bold;">${price:,.2f}&nbsp;{sign}{pct:.1f}%{sess_tag}{anchor}</span>)'
                    text = text.replace(word, flair)
                    break 
        return text

    def synthesize_dossier(self, news_db, prices, master_data, sentiment):
        nlp = LocalIntelligenceSynthesizer()
        nlp.update_vibe_lexicon(sentiment)
        gold = "#f59e0b"; text_bright = "#f8fafc"; accent = "#60a5fa"
        
        agg = MacroAggregator()
        macro_headlines = asyncio.run(agg.fetch_agg())
        
        print(f"[INFO] NLP Processor: Analyzing {len(macro_headlines)} headlines for institutional relevance...")
        # Real-world NLP Intelligence Synthesis for Executive Summary
        # V23.69 Filter: Pull more for the pool, then rank the best 15
        best_headlines = nlp.rank_news_relevance(macro_headlines, top_n=15)
        
        if best_headlines:
            top_t = best_headlines[0].get('title', 'Unknown')
            print(f"[INFO] [ALPHA] Lead Intelligence: {top_t[:70]}...")
        
        m_fg = int(sentiment.get('market', {}).get('value', 50))
        vibe_status = "NEUTRAL / CHOPPY" if 40 <= m_fg <= 60 else ("RISK-ON / ACCUMULATING" if m_fg > 60 else "RISK-OFF / PROTECTING")
        
        # 3. Intelligent Narrative Synthesis (JIT Scrape + NLP)
        scraper = LiveBlogScraper()
        scraped_lead, lead_url = asyncio.run(scraper.get_sovereign_narrative())
        if scraped_lead:
            print(f"[MACRO] Scraped Live Narrative: {lead_url}")
        
        intel_text, used_links = nlp.synthesize_market_narrative(best_headlines, vibe_status, scraped_lead=scraped_lead)
        
        # Institutional Summary Layout - Standardized with primary header classes (V23.72)
        summary_hdr_style = f'color:{text_bright}; font-size:42px; font-weight:900; letter-spacing:-1.5px; text-transform:uppercase; line-height:1.1; margin-bottom:12px;'
        if intel_text:
            exec_summary = f'<div class="hdr-title" style="{summary_hdr_style}">EXECUTIVE SUMMARY: <span style="color:{accent};">INTEL SUMMARY</span></div><div style="font-size:16px; color:{text_bright}; line-height:1.6;">{intel_text}</div>'
        else:
            exec_summary = f'<div class="hdr-title" style="{summary_hdr_style}">EXECUTIVE SUMMARY: <span style="color:{accent};">INTEL SUMMARY</span></div><div style="font-size:16px; color:{text_bright}; line-height:1.6;">The session is carving out a {vibe_status} posture (F&G: {m_fg}). Liquidity is shifting across tech sectors.</div>'
        
        # V23.91: Cross-Section Deduplication
        # 4. Prune corpus for the supporting list (remove items used in narrative)
        # If we have a lead_url, ensure it's "used" if it matches anything in the corpus
        if lead_url:
            for art in best_headlines:
                if art.get('link') == lead_url:
                    used_links.add(lead_url)

        pruned_news = [art for art in best_headlines if art.get('link') not in used_links][:20]

        macro_intel_rows = ""
        earnings_intel_rows = ""
        row_count = 0
        earn_count = 0
        
        for i, res in enumerate(pruned_news):
             f_title = self.inject_price_flair(res["title"], prices, master_data)
             
             # V24.1: Separate Earnings Area Logic
             is_earn = res.get('is_earnings') or "EARNINGS" in res.get('raw_title', '').upper() or res.get('source') == "CNBC Earnings"
             
             if is_earn and earn_count < 8:
                 row_color = gold
                 earnings_intel_rows += f'<div style="padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); color:{row_color}; font-weight:600;"><span style="font-size:14px;">📊</span>&nbsp;<a href="{res["link"]}" style="color:{row_color}; text-decoration:none !important; font-size:14px;">{f_title}</a></div>'
                 earn_count += 1
             else:
                 row_color = "#60a5fa" if row_count % 2 == 0 else "#4ade80" 
                 macro_intel_rows += f'<div style="padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); color:{row_color};"><span style="font-size:14px;">&bull;</span>&nbsp;<a href="{res["link"]}" style="color:{row_color}; text-decoration:none !important; font-size:14px;">{f_title}</a></div>'
                 row_count += 1
             
             if (row_count + earn_count) >= 20: break
             
        # Wrap earnings in a dedicated area if present
        if earnings_intel_rows:
            earnings_area = f'<div style="margin-bottom:20px; padding:12px; background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.2); border-radius:8px;"><div style="color:{gold}; font-size:18px; font-weight:900; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;">🚨 Earnings Intelligence</div>{earnings_intel_rows}</div>'
            macro_intel_rows = earnings_area + macro_intel_rows

        # Watchlist Intel Logic (V23.55)
        watchlist_intel_html = "" # Minimal fallback for now to ensure recovery stability
        
        return [], [], vibe_status, watchlist_intel_html, exec_summary, macro_intel_rows

    def gather_all_data(self, custom_tickers=None):
        master = self._load_json("CPO_MASTER_DATA.json")
        prices_path = self.db_path / "live_prices.json"
        
        # V23.86: Price Freshness Governance
        # V23.88: Session Transition Intelligence
        # We refresh if:
        # 1. Prices are > 5 minutes old (Standard TTL)
        # 2. Market has transitioned sessions (e.g., PRE -> LIVE) since last fetch
        prices = {}
        if prices_path.exists():
            try:
                raw_prices = self._load_json("live_prices.json")
                # Detect session of the last fetch
                sample = next(iter([v for k,v in raw_prices.items() if k != "_meta"]), {})
                last_fetch_type = sample.get("ext_type", "UNKNOWN")
                current_sess = self.get_market_session()
                
                # Logic: If last was PRE and now is LIVE, or last was REG/LIVE and now is POST, force refresh.
                session_changed = (last_fetch_type == "PRE" and current_sess == "LIVE") or \
                                 (last_fetch_type == "LIVE" and current_sess == "AH") or \
                                 (last_fetch_type == "UNKNOWN")
                
                stale_time = (time.time() - prices_path.stat().st_mtime) > 300
                
                if stale_time or session_changed:
                    reason = "STALE" if stale_time else f"SESSION TRANSITION ({last_fetch_type} -> {current_sess})"
                    print(f"[INFO] [CACHE] Refresh Triggered: {reason}. Hardening live data...")
                    try:
                        from live_prices import async_run_fetch
                        all_to_fetch = list(set(master.keys()) | set([t.upper() for t in (custom_tickers or [])]))
                        # V24.4: Force Freshness for Email Dossier (Ignore 15m Cache)
                        prices = asyncio.run(async_run_fetch(tickers=all_to_fetch[:250], skip_sync=True, force=True))
                        print(f"[INFO] [LIVE] JIT Refresh Complete: {len(prices)} tickers.")
                    except Exception as e:
                        print(f"[WARN] Price refresh failed: {e}. Falling back to disk.")
                        prices = raw_prices
                else:
                    prices = raw_prices
                    print(f"[INFO] [CACHE] Prices Fresh: {int(300 - (time.time() - prices_path.stat().st_mtime))}s / Session: {current_sess}")
            except Exception as e:
                print(f"[WARN] Cache analysis failed: {e}. Forcing fresh fetch.")
                prices = self._load_json("live_prices.json")
        else:
            prices = self._load_json("live_prices.json")

        news_db = self._load_json("YAHOO_NEWS_DB.json").get("news", {})
        sentiment = self.fetch_sentiment()
        
        print(f"[INFO] Analyzing Coverage: {len(master)} Master Tickers // {len(custom_tickers or [])} Custom Overrides.")
        
        tradeable = {"semi": [], "ai": [], "watchlist": []}; strategic = []
        custom_set = set([t.upper() for t in custom_tickers]) if custom_tickers else set()
        
        for sym in (set(master.keys()) | custom_set):
            res = master.get(sym, {}).get("human_research", {})
            p_data = prices.get(sym, {})
            _, pct, _ = self.get_session_data(p_data, sym)
            item = {"symbol": sym, "name": res.get("Company") or sym, "pct": pct or 0, "notes": res.get("Notes", ""), "alpha": float(res.get("Alpha Score", 0) or 0)}
            
            if sym in custom_set: tradeable["watchlist"].append(item)
            elif "semi" in (res.get("Role") or "").lower(): tradeable["semi"].append(item)
            else: tradeable["ai"].append(item)

        for k in tradeable: tradeable[k].sort(key=lambda x: x['pct'], reverse=True)
        return tradeable, strategic, prices, news_db, sentiment, master

    def compose_html(self, tradeable, strategic, prices, news_db, sentiment, master):
        # Design Tokens — matched to main site (#020617 deep navy base)
        bg_main    = "#020617"  # site --bg-main
        bg_surface = "#0f172a"  # site --bg-card
        bg_accent  = "#1e293b"  # site card inner / border layer
        bg_deep    = "#0a0f1e"  # mid-layer (F&G boxes)
        text_dim   = "#8f9bb3"
        text_bright = "#f8fafc"
        bull  = "#10b981"  # green — matches site var(--green)
        bear  = "#f43f5e"  # red   — matches site var(--danger)
        accent = "#6366f1" # indigo — close to site var(--accent)
        gold  = "#f59e0b"  # amber — site var(--gold)
        border = "#1e293b" # site border line
        
        # V23.87: Dynamic Session detection for Global Header
        sess_now = self.get_market_session()
        session = "WEEKEND INTEL" if self.now.weekday() >= 5 and not sess_now else f"MARKET {sess_now}" if sess_now else "MARKET CLOSED"
        
        # Sentiment Calculations
        market_fg = int(sentiment.get('market', {}).get('value', 50))
        crypto_fg = int(sentiment.get('crypto', {}).get('value', 50))
        
        def get_fg_color(v):
            if v <= 25: return bear # Extreme Fear
            if v <= 45: return "#ff9f1c" # Fear
            if v <= 55: return text_dim # Neutral
            if v <= 75: return bull # Greed
            return "#6ee7b7" # Extreme Greed (site green-300)

        fg_color_total = get_fg_color(market_fg)
        fg_color_crypto = get_fg_color(crypto_fg)

        # 2. Market Pulse — Comparative Divergence Section (Cash vs Futures)
        def get_diff_str(price, pct, clr, fs="8px"):
            if not price or pct is None: return ""
            prev = price / (1 + pct/100)
            diff = price - prev
            sign = "+" if diff >= 0 else ""
            return f'<div class="pulse-diff" style="font-size:{fs}; color:{clr}; opacity:0.8; font-weight:bold; margin-top:1px;">{sign}{diff:,.0f} pts</div>'
        COMPARATIVE_INDICES = [
            {"name": "S&P 500", "cash": "^GSPC", "fut": "ES=F"},
            {"name": "NASDAQ",  "cash": "^IXIC", "fut": "NQ=F"},
            {"name": "DOW 30",  "cash": "^DJI",  "fut": "YM=F"}
        ]
        
        # Dynamic Market Labels
        is_live_main = self.get_market_session() in ("LIVE", "AH")
        is_futures_active = (self.now.weekday() == 6 and self.now.hour >= 18) or (self.now.weekday() < 5)
        
        prior_close_label = "FRIDAY CLOSE" if self.now.weekday() in [0, 5, 6] else "PRIOR CLOSE"
        live_label = "SUNDAY FUTURES" if self.now.weekday() == 6 and is_futures_active else "PREMARKET" if (7 <= self.now.hour < 9) else "LIVE FUTURES" if is_futures_active else "WEEKEND STASIS"
        label_color = gold if is_futures_active else text_dim
        
        pulse_rows = []
        def render_tile(symbol, name, val, pct, sess, color):
            tag_style = "text-decoration:none;"
            if sess in ('PRE', 'AH', 'POST'): tag_style = "text-decoration:underline;"
            val_str = f"{val:,.0f}" if val > 1000 else f"{val:.2f}"
            
            return (
                f'<td width="33%" style="padding:3px;">'
                f'<div style="background:{bg_deep}; border-radius:5px; padding:10px 8px; text-align:center;">'
                f'<div class="crypto-label" style="color:{text_dim}; font-size:8px; margin-bottom:4px; font-weight:bold; text-transform:uppercase; {tag_style}">{name}</div>'
                f'<div class="crypto-val" style="color:{text_bright}; font-size:12px; font-weight:bold;">{val_str}</div>'
                f'{get_diff_str(val, pct, color, fs="7px")}'
                f'<div class="crypto-chg" style="color:{color}; font-size:10px; font-weight:bold;">{"+" if pct >= 0 else ""}{pct:.1f}%</div>'
                f'</div></td>'
            )

        if is_live_main:
            index_tiles = []
            for index in COMPARATIVE_INDICES:
                c_data = prices.get(index['cash'], {})
                c_val, c_chg, _ = self.get_session_data(c_data, index['cash'])
                c_color = bull if c_chg >= 0 else bear
                index_tiles.append(render_tile(index['cash'], index['name'], c_val, c_chg, "LIVE", c_color))
            pulse_grid_rows = f'<tr><td style="padding:4px;"><table width="100%" cellpadding="0" cellspacing="0"><tr>{" ".join(index_tiles)}</tr></table></td></tr>'
        else:
            # Multi-row layout for Futures tracking
            for index in COMPARATIVE_INDICES:
                c_data = prices.get(index['cash'], {})
                f_data = prices.get(index['fut'], {})
                c_val = c_data.get('price', 0); c_chg = c_data.get('change_pct', 0)
                c_color = bull if c_chg >= 0 else bear
                c_arr = '+' if c_chg >= 0 else ''
                f_val, f_chg, f_sess = self.get_session_data(f_data, index['fut'])
                
                f_color = bull if f_chg >= 0 else bear
                f_arr = '+' if f_chg >= 0 else ''
                f_bg = 'rgba(16,185,129,0.08)' if f_chg >= 0 else 'rgba(244,63,94,0.08)'
                
                pulse_rows.append(
                    f'<tr>'
                    f'<td style="padding:4px;"><div style="background:{bg_accent}; border-radius:5px; padding:12px 10px;">'
                    f'<div class="pulse-idx-name" style="color:{text_dim}; font-size:9px; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px; font-weight:bold; text-align:center;">{index["name"]}</div>'
                    f'<table width="100%" cellpadding="0" cellspacing="0"><tr>'
                    f'<td width="{"48%" if not is_live_main else "100%"}" style="{"border-right:1px solid "+border+"; padding-right:8px;" if not is_live_main else ""} text-align:center;">'
                    f'<div class="pulse-sub-label" style="color:{text_dim}; font-size:7px; margin-bottom:2px;">{prior_close_label}</div>'
                    f'<div class="pulse-val" style="color:{text_bright}; font-size:14px; font-weight:bold;">{c_val:,.0f}</div>'
                    f'{get_diff_str(c_val, c_chg, c_color)}'
                    f'<div class="pulse-chg" style="color:{c_color}; font-size:10px; font-weight:bold;">{c_arr}{c_chg:.1f}%</div>'
                    f'</td>'
                    f'<td width="52%" style="padding-left:12px; text-align:center;">'
                    f'<div class="pulse-sub-label" style="color:{label_color}; font-size:7px; font-weight:bold; margin-bottom:2px;">{live_label}</div>'
                    f'<div class="pulse-val" style="color:{text_bright}; font-size:14px; font-weight:bold;">{f_val:,.0f}</div>'
                    f'{get_diff_str(f_val, f_chg, f_color)}'
                    f'<div class="pulse-chg-pill" style="display:inline-block; background:{f_bg}; color:{f_color}; font-size:11px; padding:2px 6px; border-radius:3px; font-weight:bold; margin-top:2px;">{f_arr}{f_chg:.1f}%</div>'
                    f'</td>'
                    f'</tr></table>'
                    f'</div></td>'
                    f'</tr>'
                )
            pulse_grid_rows = "\n".join(pulse_rows)

        pulse_rows = []
        def render_tile(symbol, name, val, pct, sess, color):
            tag_style = "text-decoration:none;"
            if sess in ('PRE', 'AH', 'POST'): tag_style = "text-decoration:underline;"
            val_str = f"{val:,.0f}" if val > 1000 else f"{val:.2f}"
            
            return (
                f'<td width="33%" style="padding:3px;">'
                f'<div style="background:{bg_deep}; border-radius:5px; padding:10px 8px; text-align:center;">'
                f'<div class="crypto-label" style="color:{text_dim}; font-size:8px; margin-bottom:4px; font-weight:bold; text-transform:uppercase; {tag_style}">{name}</div>'
                f'<div class="crypto-val" style="color:{text_bright}; font-size:12px; font-weight:bold;">{val_str}</div>'
                f'{get_diff_str(val, pct, color, fs="7px")}'
                f'<div class="crypto-chg" style="color:{color}; font-size:10px; font-weight:bold;">{"+" if pct >= 0 else ""}{pct:.1f}%</div>'
                f'</div></td>'
            )

        if is_live_main or is_futures_active:
            index_tiles = []
            for index in COMPARATIVE_INDICES:
                # V23.85: Switch to Futures during extended hours
                target_ticker = index['cash'] if is_live_main else index['fut']
                c_data = prices.get(target_ticker, {})
                # Safely extract session data
                c_val, c_chg, c_sess = self.get_session_data(c_data, target_ticker)
                c_color = bull if (c_chg or 0) >= 0 else bear
                
                # For indices, session label is extra crucial
                label = "LIVE" if is_live_main else c_sess
                index_tiles.append(render_tile(target_ticker, index['name'], c_val or 0, c_chg or 0, label, c_color))
            pulse_grid_rows = f'<tr><td style="padding:4px;"><table width="100%" cellpadding="0" cellspacing="0"><tr>{" ".join(index_tiles)}</tr></table></td></tr>'
        else:
            pulse_grid_rows = "\n".join(pulse_rows)

        # 2b. Crypto Pulse Row
        crypto_tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD']
        crypto_tiles = []
        for t in crypto_tickers:
            p = prices.get(t, {})
            val, chg, sess = self.get_session_data(p, t)
            color = bull if chg >= 0 else bear
            crypto_tiles.append(render_tile(t, t.split('-')[0], val, chg, sess, color))
        crypto_pulse_row = f'<tr><td style="padding:4px;"><table width="100%" cellpadding="0" cellspacing="0"><tr>{" ".join(crypto_tiles)}</tr></table></td></tr>'
        # 2b. Global sentinel — 2-per-row tiles
        global_map = [('HSI', '^HSI'), ('NIKKEI', '^N225'), ('DAX', '^GDAXI'), ('FTSE', '^FTSE')]
        global_tiles = []
        hr = self.now.hour
        for name, ticker in global_map:
            p = prices.get(ticker, {})
            val, chg, sess = self.get_session_data(p, ticker)
            color = bull if chg >= 0 else bear
            arrow = '▲' if chg >= 0 else '▼'
            is_open = (
                (ticker in ('^HSI', '^N225') and (hr >= 20 or hr <= 4)) or
                (ticker in ('^GDAXI', '^FTSE') and (3 <= hr <= 11))
            )
            badge = f'<span style="color:{bull}; font-size:10px; font-weight:bold;">● LIVE</span>' if is_open else f'<span style="color:{bear}; font-size:10px; font-weight:bold;">● CLOSED</span>'
            chg_bg = 'rgba(16,185,129,0.08)' if chg >= 0 else 'rgba(244,63,94,0.08)'
            global_tiles.append(
                f'<td class="tile-cell" style="width:50%; padding:3px; vertical-align:top;">'
                f'<div style="background:{bg_accent}; border-radius:5px; padding:12px 10px; text-align:center;">'
                f'<div class="global-badge" style="margin-bottom:4px;">{badge}</div>'
                f'<div class="global-label" style="font-family:sans-serif; color:{text_dim}; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">{name}</div>'
                f'<div class="global-chg" style="background:{chg_bg}; border-radius:3px; padding:4px 0; font-family:monospace; color:{color}; font-size:15px; font-weight:bold;">'
                f'{arrow}{abs(chg):.1f}%'
                f'<div style="font-size:9px; opacity:0.8; margin-top:2px;">{get_diff_str(p.get("price",0), chg, color, fs="9px")}</div>'
                f'</div>'
                f'</div></td>'
            )

        global_grid_rows = ""
        for i in range(0, len(global_tiles), 2):
            pair = global_tiles[i:i+2]
            if len(pair) == 1: pair.append('<td class="tile-cell" style="width:50%; padding:3px;"></td>')
            global_grid_rows += f'<tr>{"".join(pair)}</tr>'

        # 2c. Session Performance Carve-out — Responsive High-Density Tiles (V23.50)
        perf_candidates = []
        for sym, p_data in prices.items():
            if sym == '_meta' or not self.is_legit_ticker(sym): continue
            price, pct, sess = self.get_session_data(p_data, sym)
            if pct is not None and abs(pct) > 0.05: # filter noise
                perf_candidates.append({'symbol': sym, 'price': price, 'change_pct': pct, 'session': sess})
        
        # Gainers: Greatest to Least
        gainers_top = sorted([p for p in perf_candidates if p['change_pct'] > 0], key=lambda x: x['change_pct'], reverse=True)[:10]
        # Losers: Most Negative to Least Negative
        losers_top = sorted([p for p in perf_candidates if p['change_pct'] < 0], key=lambda x: x['change_pct'])[:10]

        def render_perf_list(movers, title, color):
            """Renders Movers with centered-block but left-aligned symbols."""
            results = []
            # Split into two columns for top 10
            mid = (len(movers) + 1) // 2
            col1 = movers[:mid]
            col2 = movers[mid:]
            
            for sub_movers in [col1, col2]:
                if not sub_movers: 
                    results.append('<td width="50%"></td>')
                    continue

                items_html = []
                for s in sub_movers:
                    pct_val = s.get('change_pct', 0)
                    price_val = s.get('price', 0)
                    sym = s['symbol']
                    p_entry = prices.get(sym, {})
                    sess = s.get('session', 'LIVE')
                    
                    color_movers = bull if pct_val >= 0 else bear
                    pct_str = f"{'+' if pct_val >= 0 else ''}{pct_val:.2f}%"
                    price_str = f"${price_val:,.2f}" if price_val > 0 else ""
                    
                    # V24.3: Session-Aware Anchoring & Scaled Typography
                    anchor = ""
                    pct_fs = "18px"
                    tag_fs = "8px"
                    
                    if sess in ["PRE", "AH", "OVN", "POST"]:
                        c_p = p_entry.get("close_price") or p_entry.get("price")
                        if c_p: anchor = f'<span style="font-size:9px; color:#94a3b8; font-weight:normal;">&nbsp;| C: ${c_p:,.2f}</span>'
                        pct_fs = "14px" # Smaller per user request
                        tag_fs = "7px"
                        
                    badge = self.get_session_tag_html(fs=tag_fs, sess_override=sess)
                    symbol_link = f'<a href="https://finance.yahoo.com/quote/{sym}" style="color:#f59e0b; text-decoration:none;">${sym}</a>'
                    
                    items_html.append(f'''
                        <div style="margin-bottom:2px; text-align:center;">
                            <div class="perf-item" style="display:inline-block; width:98%; max-width:380px; background:rgba(255,255,255,0.02); padding:4px 12px; border-radius:3px; font-family:monospace; font-size:18px; text-align:left; vertical-align:middle; white-space:nowrap; overflow:hidden;">
                                <span style="display:inline-block; min-width:80px; color:#f59e0b; font-weight:bold;">{symbol_link}</span>
                                <span style="display:inline-block; min-width:85px; color:#cbd5e1; font-size:12px; opacity:0.8; text-align:right; margin-right:15px; vertical-align:middle;">{price_str}</span>
                                <span style="display:inline-block; color:{color_movers}; font-weight:900; font-size:{pct_fs}; vertical-align:middle;">{pct_str}&nbsp;{badge}{anchor}</span>
                            </div>
                        </div>''')

                results.append(f"""
                    <td class="perf-cell" width="50%" style="vertical-align:top; padding:0 2px; text-align:center;">
                        <div class="perf-hdr" style="color:{color}; font-size:10px; font-weight:900; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;">{title}</div>
                        {''.join(items_html)}
                    </td>
                """)
            return "".join(results)

        # V23.60: High-Density Gainer/Loser Grid
        perf_carveout_html = f"""
        <tr><td style="padding:15px 0 25px 0;">
            <div class="section-hdr" style="font-family:monospace; font-size:20px; letter-spacing:5px; text-transform:uppercase; font-weight:bold; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.1); text-align:center; color:{text_bright};">Session Performance Movers</div>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr><td colspan="2" style="font-size:16px; color:{bull}; font-weight:900; text-align:center; padding-bottom:12px; text-transform:uppercase; letter-spacing:2px;">▲ Top Gainers</td></tr>
                <tr>{render_perf_list(gainers_top, "", bull)}</tr>
                <tr><td colspan="2" style="padding-top:25px; font-size:16px; color:{bear}; font-weight:900; text-align:center; padding-bottom:12px; text-transform:uppercase; letter-spacing:2px;">▼ Top Losers</td></tr>
                <tr>{render_perf_list(losers_top, "", bear)}</tr>
            </table>
        </td></tr>
        """

        # 3. Narrative Intelligence
        macro_ps, sector_ps, sentiment_label, watchlist_intel_html, exec_summary, macro_intel_rows = self.synthesize_dossier(news_db, prices, master, sentiment)
        macro_html = "".join([
            f'<div style="color:{text_dim}; font-size:15px; line-height:1.7; margin-bottom:14px; white-space:normal !important; overflow:visible !important;">'
            f'{p}</div>' for p in macro_ps
        ])

        def render_bucket(title, items, hide_notes=False, columns=1):
            if not items: return ""
            rows = []
            for t in items:
                sym = t.get('symbol', '').replace('$', '')
                p_entry = prices.get(t['symbol'], {})
                price, pct, sess = self.get_session_data(p_entry, t['symbol'])
                has_price = price and price > 0
                
                if not has_price:
                    pct_display = '<span style="color:#4a5568; font-size:9px;">N/A</span>'
                    clr = text_dim
                else:
                    clr = bull if pct >= 0 else bear
                    sess_tag = self.get_session_tag_html(fs="8px", sess_override=sess)
                    
                    anchor = ""
                    if sess in ["PRE", "AH", "OVN", "POST"]:
                        c_p = p_entry.get("close_price") or p_entry.get("price")
                        if c_p: anchor = f'<span style="font-size:9px; color:#94a3b8; font-weight:normal;">&nbsp;| C: ${c_p:,.2f}</span>'
                    
                    price_str = f'<span style="color:#cbd5e1; font-size:13px; margin-right:8px;">${price:,.2f}</span>'
                    pct_display = f'{price_str}<span style="color:{clr}; font-weight:bold; font-size:14px;">{pct:+.2f}%{sess_tag}{anchor}</span>'

                notes = "" if hide_notes else t.get('notes', '').strip()
                flaired_notes = self.inject_price_flair(notes, prices, link=False)
                display_name = t['name'] if t['name'].upper() != sym.upper() else self.ticker_name_map.get(sym, "")

                rows.append(f"""
                    <div style="background:rgba(255,255,255,0.03); border-left:3px solid {clr}; padding:5px 12px; border-radius:4px; margin-bottom:4px;">
                        <table width="100%" cellpadding="0" cellspacing="0"><tr>
                            <td width="35%" style="font-family:monospace; font-weight:bold; font-size:18px;"><a href="https://finance.yahoo.com/quote/{t['symbol']}" style="color:{gold}; text-decoration:none;">${sym}</a></td>
                            <td width="65%" style="text-align:right; font-family:monospace;">{pct_display}</td>
                        </tr></table>
                        {f'<div style="font-size:12px; color:#8f9bb3; margin-top:6px; line-height:1.6; overflow:hidden; max-height:80px;">{flaired_notes}</div>' if flaired_notes else ''}
                    </div>
                """)
            
            # If 2 cols, shard the rows
            if columns == 2:
                half = (len(rows) + 1) // 2
                col1 = "".join(rows[:half])
                col2 = "".join(rows[half:])
                content = f'<table width="100%" cellpadding="0" cellspacing="0"><tr><td width="50%" style="vertical-align:top; padding-right:4px;">{col1}</td><td width="50%" style="vertical-align:top; padding-left:4px;">{col2}</td></tr></table>'
            else:
                content = "".join(rows)

            return (
                f'<div style="margin-top:10px;">'
                f'<div class="section-hdr" style="color:{text_dim}; font-family:monospace; font-size:20px; letter-spacing:2px; text-transform:uppercase; font-weight:bold; margin-bottom:6px; padding-bottom:4px; border-bottom:1px solid #1e2130;">— {title} —</div>'
                f'{content}</div>'
            )

        watchlist_html = render_bucket("Real-time Watchlist", tradeable.get("watchlist", []), hide_notes=True, columns=2)
        # Merge Semi and AI - Limit total dashboard to Top 25 to avoid Gmail clipping
        merged_intel = (tradeable.get("semi", []) + tradeable.get("ai", []))[:25]
        intelligence_html = render_bucket("Sovereign Intelligence Dashboard", merged_intel, columns=1)

        # Master Template Assembly — Responsive Dual-Surface Design
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ margin:0; padding:0; background-color:{bg_main}; }}
                .wrap {{ background-color:{bg_main}; padding:20px 16px; }}
                .main-table {{ max-width:600px; width:100%; margin:0 auto; }}
                .tile-cell {{ width:50%; padding:3px; vertical-align:top; }}

                /* Desktop: side-by-side cockpit */
                .pulse-left {{ width:55%; padding-right:18px; vertical-align:top; }}
                .pulse-right {{ width:45%; padding-left:18px; vertical-align:top; border-left:1px solid {border}; }}

                /* Mobile overrides */
                @media only screen and (max-width:520px) {{
                    .wrap {{ padding:8px !important; }}
                    .pulse-left, .pulse-right {{
                        display:block !important;
                        width:100% !important;
                        padding-left:0 !important;
                        padding-right:0 !important;
                        border-left:none !important;
                        border-top:1px solid {border};
                        padding-top:14px !important;
                        margin-top:14px !important;
                    }}
                    .pulse-left {{ border-top:none !important; margin-top:0 !important; padding-top:0 !important; }}
                    .header-cell {{ display:block !important; width:100% !important; text-align:left !important; padding-bottom:6px; }}
                    .badge-cell {{ display:block !important; width:100% !important; text-align:left !important; padding-bottom:0; }}
                    .sector-card {{ padding:10px !important; }}
                    .global-chip {{ display:block !important; width:100% !important; margin-bottom:10px; }}
                    .fg-left, .fg-right {{ width:50% !important; }}
                    /* MOBILE: 6-column side-by-side Movers */
                    .perf-cell {{ display:table-cell !important; width:50% !important; padding:4px !important; text-align:center !important; }}
                    .perf-hdr {{ font-size:11px !important; margin-bottom:10px !important; }}
                    .perf-item {{ font-size:11px !important; padding:6px 8px !important; }}
                }}

                /* Desktop / large screen upsizing */
                @media only screen and (min-width:600px) {{
                    .main-table {{ max-width:850px !important; }}
                    /* Section headers --- bold, large, prominent */
                    .section-hdr {{
                        font-size:16px !important;
                        font-weight:900 !important;
                        letter-spacing:3px !important;
                        color:{text_bright} !important;
                    }}
                    .macro-hdr {{
                        font-size:18px !important;
                        font-weight:900 !important;
                        letter-spacing:2px !important;
                    }}
                    /* Global Markets grid labels */
                    .global-label {{ font-size:16px !important; letter-spacing:1.5px !important; }}
                    .global-chg   {{ font-size:24px !important; padding:4px 0 !important; }}
                    .global-badge {{ font-size:12px !important; }}
                    /* Sovereign Pulse & Crypto Upsizing */
                    .pulse-idx-name {{ font-size:16px !important; letter-spacing:1.5px !important; margin-bottom:15px !important; }}
                    .pulse-sub-label {{ font-size:10px !important; }}
                    .pulse-val {{ font-size:24px !important; }}
                    .pulse-chg {{ font-size:14px !important; }}
                    .pulse-chg-pill {{ font-size:14px !important; padding:4px 8px !important; }}
                    .pulse-diff {{ font-size:12px !important; margin-top:2px !important; }}
                    .crypto-label {{ font-size:13px !important; margin-bottom:6px !important; }}
                    .crypto-val   {{ font-size:24px !important; }}
                    .crypto-chg   {{ font-size:14px !important; }}
                    .fg-val       {{ font-size:32px !important; }}
                    .fg-label     {{ font-size:13px !important; }}
                    /* Sector cards */
                    .sec-ticker {{ font-size:18px !important; }}
                    .sec-name   {{ font-size:16px !important; }}
                    .sec-pct    {{ font-size:18px !important; }}
                    .sec-notes  {{ font-size:13px !important; line-height:1.6 !important; color:#8f9bb3 !important; }}
                    
                    /* TARGETED: CLOSING PRICES */
                    .sec-price {{ font-size:15px !important; font-weight:bold !important; color:{text_bright} !important; }}
                    
                    /* Velocity Override: Tighter Padding, Larger Font */
                    .vel-chip {{ font-size:16px !important; padding:8px 12px !important; }}
                    .vel-vol  {{ font-size:14px !important; }}
                    .mv-row   {{ font-size:16px !important; padding:10px 16px !important; }}
                    .mv-vol   {{ font-size:14px !important; }}
                    .top-mover-chip {{ font-size:11px !important; padding:8px 12px !important; }}
                    /* Movers: Larger Font */
                    .perf-item {{ font-size:18px !important; margin-bottom:6px !important; }}
                    .perf-hdr {{ font-size:18px !important; margin-bottom:15px !important; letter-spacing:3px !important; }}
                    .perf-cell {{ padding:0 4px !important; }}
                    /* Watchlist: Larger Font */
                    .sector-card {{ padding:14px 18px !important; }}
                    .sec-ticker {{ font-size:16px !important; }}
                    .sec-name   {{ font-size:13px !important; }}
                    .sec-pct    {{ font-size:16px !important; }}
                    .sec-notes  {{ font-size:14px !important; line-height:1.6 !important; color:#8f9bb3 !important; }}
                    
                    /* Header block */
                    .hdr-title {{ font-size:28px !important; }}
                    .hdr-sub   {{ font-size:15px !important; }}
                }}
                /* Mobile lock --- Upscaling for S&P, NASDAQ, DOW, BTC, ETH, SOL */
                @media only screen and (max-width:599px) {{
                    .section-hdr {{
                        font-size:16px !important;
                        font-weight:bold !important;
                        color:{text_bright} !important;
                        letter-spacing:1px !important;
                    }}
                    .pulse-idx-name {{ font-size:14px !important; margin-bottom:8px !important; }}
                    .pulse-sub-label {{ font-size:9px !important; }}
                    .pulse-val {{ font-size:22px !important; font-weight:900 !important; }}
                    .pulse-chg {{ font-size:14px !important; }}
                    .crypto-label {{ font-size:14px !important; margin-bottom:4px !important; }}
                    .crypto-val   {{ font-size:20px !important; font-weight:900 !important; }}
                    .crypto-chg   {{ font-size:14px !important; }}
                    .global-label {{ font-size:14px !important; }}
                    .global-chg   {{ font-size:18px !important; font-weight:bold !important; }}
                    .perf-item    {{ font-size:14px !important; }}
                    .perf-cell    {{ padding:0 6px !important; }}
                    /* Mobile header reduction by 35% (42px -> 27px) */
                    .hdr-title    {{ font-size:27px !important; }}
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
                        <div style="color:{text_dim}; font-size:10px; font-family:monospace; margin-top:8px; letter-spacing:1px;">V23.86 // {self.now.strftime('%a %Y-%m-%d %H:%M EST')} // {session}</div>
                    </td>
                    <td class="badge-cell" style="text-align:right; white-space:nowrap; vertical-align:middle; padding-left:10px;">
                        <span style="background:{accent}; color:#fff; padding:4px 10px; font-size:9px; border-radius:2px; font-weight:bold; letter-spacing:1px;">CONFIDENCE: HIGH</span>
                    </td>
                </tr></table>
            </td></tr>

            <!-- ═══ PULSE BLOCK ═══ -->
            <tr><td class="narrative-box" style="background:{bg_surface}; padding:20px 0; border-radius:6px;">

                <!-- US Markets grid -->
                <div class="section-hdr" style="font-size:20px; font-family:monospace; color:{gold}; letter-spacing:2px; text-transform:uppercase; font-weight:bold; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid rgba(245,158,11,0.2);">Sovereign Index Pulse // Divergence</div>
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;">
                    {pulse_grid_rows}
                    {crypto_pulse_row}
                    
                    <!-- Fear & Greed — centered 2-col -->
                    <tr><td style="padding:10px 0 15px 0;">
                        <table width="100%" cellpadding="0" cellspacing="0"><tr>
                            <td width="50%" style="padding:3px; vertical-align:top;">
                                <div style="background:#0a0f1e; border-radius:5px; padding:12px 8px; text-align:center;">
                                    <div class="fg-label" style="font-size:8px; font-family:monospace; color:#8f9bb3; letter-spacing:1px; margin-bottom:3px;">MARKET F&G</div>
                                    <div class="fg-val" style="font-size:32px; font-weight:900; color:{fg_color_total}; line-height:1;">{market_fg}</div>
                                    <div style="font-size:7px; color:#8f9bb3; margin-top:2px;">FEAR & GREED</div>
                                </div>
                            </td>
                            <td width="50%" style="padding:3px; vertical-align:top;">
                                <div style="background:#0a0f1e; border-radius:5px; padding:12px 8px; text-align:center;">
                                    <div class="fg-label" style="font-size:8px; font-family:monospace; color:#8f9bb3; letter-spacing:1px; margin-bottom:3px;">CRYPTO F&G</div>
                                    <div class="fg-val" style="font-size:32px; font-weight:900; color:{fg_color_crypto}; line-height:1;">{crypto_fg}</div>
                                    <div style="font-size:7px; color:#8f9bb3; margin-top:2px;">COIN GLASS</div>
                                </div>
                            </td>
                        </tr></table>
                    </td></tr>
                </table>

                <!-- Global Markets grid -->
                <div class="section-hdr" style="font-size:20px; font-family:monospace; color:{text_dim}; letter-spacing:2px; text-transform:uppercase; font-weight:bold; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid {border};">Global Markets</div>
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;">{global_grid_rows}</table>

                {perf_carveout_html}
                
                <!-- Macro Intelligence leads the news flow -->
                <div style="margin-top:25px;">
                    <div class="section-hdr" style="font-family:monospace; font-size:20px; letter-spacing:3px; text-transform:uppercase; font-weight:bold; margin-bottom:12px; display:inline-block; border-bottom:2px solid {accent}; padding-bottom:4px; color:{accent};">I. MACRO // GLOBAL PULSE</div>
                    <div style="background:rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.05); padding:15px; border-radius:4px; margin-bottom:20px;">
                        {exec_summary}
                        <div style="font-size:13px; font-family:monospace; color:{text_bright}; margin-top:20px;">
                            {macro_intel_rows}
                        </div>
                    </div>
                </div>

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
                        SOVEREIGN ENGINE HARDENED // AUTO-GENERATED BY GIGACPO V23.87
                    </div>
                </td></tr>
            </table>
            </center>
        </body></html>
        """
        # V23.60: Gmail Clipping Defense (Minification)
        # Strips redundant spaces, tabs, and newlines between tags.
        minified = re.sub(r'>\s+<', '><', html)
        minified = re.sub(r'<!--.*?-->', '', minified, flags=re.DOTALL)
        return minified

    def send_email(self, html, subject_override=None):
        u = os.getenv("GMAIL_USER")
        pk = os.getenv("GMAIL_APP_PASS")
        r = os.getenv("RECIPIENT_EMAIL", "rayjonesy@gmail.com")
        display_name = os.getenv("GMAIL_DISPLAY_NAME", "Market News")
        
        salt = uuid.uuid4().hex[:8]
        msg = MIMEMultipart()
        msg['From'] = f"{display_name} <{u}>"
        msg['To'] = r
        msg['Subject'] = subject_override if subject_override else f"Market Insights and Sovereign Intel // {self.now.strftime('%m/%d/%y')} [{salt}]"
        html_anti_clip = html.replace('</body>', f'<div style="display:none; color:transparent; font-size:0px; height:0px;">Anti-clip UUID: {uuid.uuid4().hex} - Time: {datetime.datetime.now().isoformat()}</div></body>')
        msg.attach(MIMEText(html_anti_clip, 'html'))
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s: s.login(u, pk); s.send_message(msg)
            print("[OK] DISPATCHED."); return True
        except Exception as e: print(f"[FAIL] {e}"); return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GIGACPO Intelligence Dossier Engine")
    parser.add_argument("--test-email", action="store_true", help="Send a test email")
    parser.add_argument("--tickers", type=str, help="Comma-separated list of custom tickers")
    args, unknown = parser.parse_known_args()

    custom_tickers = []
    if args.tickers:
        if args.tickers.endswith(".txt") and os.path.exists(args.tickers):
            with open(args.tickers, "r") as f:
                content = f.read()
                # Support newlines, spaces, and commas
                raw = content.replace('\n', ',').replace(' ', ',')
                custom_tickers.extend([t.strip().upper() for t in raw.split(',') if t.strip()])
        else:
            custom_tickers.extend([t.strip().upper() for t in args.tickers.split(',') if t.strip()])
    
    # Also support free-floating flags like --NVDA or trailing lists
    for u in unknown:
        if u.startswith("--") and len(u) > 2:
            t = u[2:].upper().replace(',', ' ').split()[0]
            custom_tickers.append(t)
        elif not u.startswith("-"):
            for t in u.split(','):
                t = t.strip().upper()
                if t: custom_tickers.append(t)

    # V23.48: Trigger Sparkline Sidecar Fetch (Async but isolated)
    try:
        try:
            from email_spark_fetcher import run_spark_fetch
        except ImportError:
            from engine.email_spark_fetcher import run_spark_fetch
        
        # Global 15m check before even hitting the sidecar
        spark_path = Path(__file__).parent.parent / 'database' / 'email_sparklines.json'
        stale_for_sidecar = []
        log.info("Skipping Email Sparkline Sidecar (Disabled)")
    except Exception as e:
        log.warning(f"Sparkline sidecar failed: {e}")

    def ts(): return datetime.datetime.now().strftime("%H%M")

    print(f"[{ts()}] # V23.87: Sovereign Intelligence Engine — Unified Session Pulse (EST)")
    engine = SovereignIntelligenceEngine()
    print(f"[{ts()}] [DEBUG] Engine initialized.")
    
    # Filter custom tickers to legit ones
    print(f"[{ts()}] [DEBUG] Filtering custom tickers...")
    valid_custom = [t for t in custom_tickers if engine.is_legit_ticker(t)]
    if valid_custom:
        print(f"[{ts()}] [CLI] Custom Watchlist: {', '.join(valid_custom)}")

    print(f"[{ts()}] [DEBUG] Gathering all data...")
    tradeable, strategic, prices, news_db, sentiment, entries = engine.gather_all_data(custom_tickers=valid_custom)
    print(f"[{ts()}] [DEBUG] Data gathered. Composing HTML...")
    html = engine.compose_html(tradeable, strategic, prices, news_db, sentiment, entries)
    
    # Aggressive Minification for Gmail (102KB Limit)
    import re
    html = re.sub(r'>\s+<', '><', html) 
    html = re.sub(r'\s{2,}', ' ', html)
    html = html.replace('\n', '').replace('\r', '')
    
    preview_path = engine.db_path / "synopsis_preview.html"
    with open(preview_path, "w", encoding="utf-8") as f: 
        f.write(html)
    
    payload_kb = len(html)/1024
    print(f"Dossier generated: {preview_path}")
    print(f"Payload Size: {payload_kb:.1f} KB {'[OVER LIMIT - WILL CLIP]' if payload_kb > 102 else '[SAFE]'}")

    if args.test_email:
        import hashlib
        session_hash = hashlib.md5(html.encode()).hexdigest()[:8].upper()
        subject = f"Market Insights and Intel // {engine.now.strftime('%Y-%m-%d')} // [{session_hash}]"
        engine.send_email(html, subject_override=subject)
        print(f"[EMAIL] Intelligence Dispatched: {subject}")
