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
try:
    from live_prices import async_run_fetch, load_tickers
    from local_nlp import LocalIntelligenceSynthesizer
    from email_spark_fetcher import run_spark_fetch
except ImportError:
    from engine.live_prices import async_run_fetch, load_tickers
    from engine.local_nlp import LocalIntelligenceSynthesizer
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
        """Returns the current time normalized to US/Eastern (EDT/EST)."""
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        # Simplified 2026 DST Hack: April is EDT (UTC-4)
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

    def get_market_session(self, symbol=None):
        # V22.93: Precise Session Detection + Overnight Awareness
        # V23.47: Suffix-Aware Global Exchange Logic
        hr = self.now.hour; mn = self.now.minute
        tm = hr * 60 + mn
        day = self.now.weekday()
        
        # 1. Crypto & Sunday Futures Override
        if symbol and symbol.endswith("-USD"): return "LIVE"
        if day == 6 and hr >= 18: return "OVN"
        if day >= 5: return "" # Weekend Stasis
        
        # 2. Exchange Hour Mapping (Normalization to EST)
        # Default: US (09:30 - 16:00)
        open_m, close_m = 570, 960
        
        if symbol:
            s_up = symbol.upper()
            # Europe (DE/ST/L/PA/MI/MC/AS): ~03:00 - 11:30 EST
            if any(s_up.endswith(s) for s in [".DE", ".ST", ".L", ".PA", ".MI", ".MC", ".AS"]):
                open_m, close_m = 180, 690 
            # Asia (HK/N225): ~21:30 - 04:00 EST
            elif any(s_up.endswith(s) for s in [".HK", ".N225", ".TW", ".KS"]):
                open_m, close_m = 1290, 240 # Spans midnight
            # Australia (AX/CX): ~19:00 - 01:00 EST
            elif any(s_up.endswith(s) for s in [".AX", ".CX"]):
                open_m, close_m = 1140, 60  # Spans midnight

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
            if 240 <= tm < open_m: return "PRE"
            # Evening Session: 4PM - 8PM EST
            if close_m <= tm < 1200: return "AH"
            # Overnight / Late Night
            if tm >= 1200 or tm < 240: return "OVN"
        return ""

    def get_session_data(self, p_data, symbol=None):
        """Unified session logic: extract correct price/pct from live_prices schema."""
        sess = self.get_market_session(symbol)
        price = p_data.get("price", 0)
        pct = p_data.get("change_pct", 0)
        
        ext_type = p_data.get("ext_type")
        # High-Fidelity: Link data to session
        if ext_type and ext_type in ["OVN", "PRE", "POST"]:
            # Prioritize matching session
            match = (ext_type == sess)
            # Aliases for same session (POST == AH, PRE == PM)
            if not match:
                match = (sess == "AH" and ext_type == "POST") or (sess == "PM" and ext_type == "PRE")
            
            # V23.01e: OVN Fallback — If we just entered PM (4AM-5AM) but only have OVN data, use OVN
            if not match and sess == "PM" and ext_type == "OVN":
                match = True

            # V23.47: LIVE status takes precedence for Regular Hours data
            if match or sess == "LIVE":
                price = p_data.get("ext_price") or price
                pct = p_data.get("ext_pct") or pct
                # Return the effective session for the UI tag
                if match: sess = ext_type
        
        return price, pct, sess

    def get_session_tag_html(self, fs="9px", color=None, sess_override=None):
        sess = sess_override if sess_override is not None else self.get_market_session()
        if not sess: return ""
        
        # V23.55: User-defined session colors
        # PRE = Orange, PM = Blue, AH = Red, OVN = Amber, LIVE = Green
        bg = "rgba(148,163,184,0.1)" # Default dim
        text_color = color if color else "#94a3b8"
        
        if sess == "PRE":
            text_color = "#f59e0b" # Orange
            bg = "rgba(245,158,11,0.1)"
        elif sess == "PM":
            text_color = "#60a5fa" # Lightened Blue (V23.58)
            bg = "rgba(96,165,250,0.1)"
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
        
        sess_tag = self.get_session_tag_html(sess_override=sess)
        
        style = f'color:{gold}; font-weight:bold; text-decoration:none;'
        pct_style = f'color:{color}; font-weight:800; text-decoration:none;'

        if simple:
            return f'<span style="{style}">{display_sym}</span> <span style="color:#cbd5e1; font-size:11px;">${price:.2f}</span> <span style="{pct_style}">{pct:+.2f}%{sess_tag}</span>'
        return f'<span style="{style}">${display_sym}</span> <span style="color:#cbd5e1; font-size:12px;">${price:.2f}</span> <span style="{pct_style}">{emoji} {pct:+.2f}%{sess_tag}</span>'

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

    def inject_price_flair(self, text, prices, master_data=None, link=True):
        """Auto-detect tickers and company names to inject live price chips."""
        if not text: return text
        
        # 1. Build Entity Map (Case-Insensitive)
        entities = {} # lower_name -> ticker
        giants = {
            "nvidia": "NVDA", "google": "GOOGL", "alphabet": "GOOGL", 
            "amazon": "AMZN", "microsoft": "MSFT", "apple": "AAPL",
            "amd": "AMD", "broadcom": "AVGO", "marvell": "MRVL",
            "meta": "META", "tesla": "TSLA", "netflix": "NFLX"
        }
        entities.update(giants)

        if master_data:
            for t, d in master_data.items():
                entities[t.lower()] = t
                if "research" in d and "company" in d["research"]:
                    entities[d["research"]["company"].lower()] = t
                elif "name" in d:
                    entities[d["name"].lower()] = t
        # From current price set (including discovered items)
        for t in prices.keys():
            entities[t.lower()] = t
            
        # Build fuzzy suffix map (e.g. tlx -> TLX.AX)
        fuzzy_prices = {}
        for full_t in prices.keys():
            base = full_t.split('.')[0].lower()
            if base not in fuzzy_prices: fuzzy_prices[base] = full_t

        # 2. Ticker/Symbol Discovery & Injection
        candidates = set(re.findall(r'\b\$?([A-Z0-9]{2,10}(?:\.[A-Z]{1,3})?)\b', text))
        candidates.update(re.findall(r'\(([A-Z0-9]{2,10}(?:\.[A-Z]{1,3})?)\)', text))
        
        alias_map = self._load_aliases()
        final_cands = {}
        for c in candidates:
            final_cands[c] = alias_map.get(c, c)
            
        processed_tickers = set()
        for sym, ticker in final_cands.items():
            if not self.is_legit_ticker(ticker): continue
            
            if ticker in prices and ticker not in processed_tickers:
                chip = self.get_ticker_chip(ticker, prices, simple=True, link=link)
                if not chip: continue
                
                new_text = text.replace(f"({sym})", f"({chip})")
                if new_text != text:
                    text = new_text
                else:
                    text, count = re.subn(rf'\b\$?{re.escape(sym)}\b', chip, text)
                processed_tickers.add(ticker)

        # 3. Name-based Search (Using Master Data + Alias Map)
        # Combine master_data names and ALIAS_MAP for exhaustive flairing
        entities = {}
        if master_data:
            for ticker, d in master_data.items():
                name = d.get("name") or d.get("research", {}).get("company")
                if name: entities[name.upper()] = ticker.upper()
        
        # Add high-confidence aliases to searchable entities
        for name, ticker in self.ALIAS_MAP.items():
            entities[name] = ticker

        # V22.7: Layer in the massive symbol bridge
        if self.ticker_name_map:
            for name, ticker in self.ticker_name_map.items():
                if name not in entities: # Don't overwrite higher-priority aliases
                    entities[name] = ticker

        sorted_names = sorted(entities.keys(), key=len, reverse=True)
        for name in sorted_names:
            ticker = entities[name]
            if len(name) < 4: continue 
            if ticker not in prices or ticker in processed_tickers: continue
            
            if name.lower() in text.lower():
                pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    orig_name = match.group(0)
                    chip = self.get_ticker_chip(ticker, prices, simple=True, link=link)
                    if not chip: continue 
                    
                    text = text.replace(orig_name, f"{orig_name} ({chip})")
                    processed_tickers.add(ticker)
        
        # 4. FINAL HARDENING: Neutralize any remaining auto-linkable intl symbols (LPK.DE)
        if not link:
            # Break common pattern: CAPITALS.CAPS (LPK.DE, ^HSI, TSMC.TW)
            text = re.sub(r'(\b[A-Z0-9]{2,10})\.([A-Z]{1,3}\b)', r'\1.&#8203;\2', text)
            # Neutralize cashtags with dots ($SIVE.ST)
            text = re.sub(r'(\$[A-Z0-9]{2,10})\.([A-Z]{1,3}\b)', r'\1.&#8203;\2', text)

        return text

    def synthesize_dossier(self, news_db, prices, master_data, sentiment):
        # 1. Prepare Discovery: Scan for all mentioned tickers in headlines first
        nlp = LocalIntelligenceSynthesizer()
        nlp.update_vibe_lexicon(sentiment)
        
        # V23.55: UI Constants
        gold = "#f59e0b"
        text_dim = "#8f9bb3"
        text_bright = "#f8fafc"
        
        macro_headlines = self.fetch_live_macro()
        # V23.55: Priority Signal Integration
        priority_headlines = asyncio.run(self.fetch_priority_signals())
        
        # Combined discovery set
        all_src = macro_headlines + priority_headlines
        
        # V23.60: Render Watchlist Intel Block
        watchlist_intel_html = ""
        if priority_headlines:
            intel_rows = []
            used_priority_icons = set()
            for item in priority_headlines:
                icon = self.get_context_icon(item['title'], used_icons=used_priority_icons)
                t_key = item["target"].upper()
                target_badge = f'<span style="color:#f59e0b; background:rgba(217,119,6,0.1); padding:2px 6px; border-radius:3px; font-weight:900; margin-right:8px; font-size:10px; border:1px solid rgba(245,158,11,0.2);">{t_key}</span>'
                flaired_title = self.inject_price_flair(item['title'], prices, master_data)
                
                # Tighten space: reduced margin-bottom from 12px to 6px
                intel_rows.append(f"""
                <div style="margin-bottom:6px; padding:10px 14px; background:rgba(255,255,255,0.02); border-radius:4px; border-left:3px solid {gold};">
                    <div style="font-size:14px; line-height:1.4;">
                        <span style="margin-right:8px; vertical-align:middle;">{icon}</span> {target_badge} <a href="{item['link']}" style="color:{text_bright}; text-decoration:none !important;">{flaired_title}</a>
                    </div>
                </div>
                """)
            
            watchlist_intel_html = f"""
            <div class="watchlist-intel-block" style="margin-bottom:30px; margin-top:20px;">
                <div class="section-hdr" style="font-family:monospace; font-size:11px; letter-spacing:4px; text-transform:uppercase; font-weight:bold; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(245,158,11,0.3); color:{gold};">📡 Watchlist Intelligence // Severe Signals</div>
                {"".join(intel_rows)}
            </div>
            """

        limit = self.now - datetime.timedelta(hours=48)
        
        # V22.30: Exhaustive multi-layer discovery
        alias_map = self._load_aliases()
        
        def extract_candidates(src_list):
            cands = set()
            for story in src_list:
                text = f"{story.get('title','')} {story.get('summary','')}"
                # Primary regex for cashtags and symbols
                raw_cands = set(re.findall(r'\b\$?([A-Z]{2,6})\b', text))
                # Parenthetical symbols common in news
                raw_cands.update(re.findall(r'\(([A-Z]{2,6})\)', text))
                
                for c in raw_cands:
                    c_up = c.upper()
                    if not self.is_legit_ticker(c_up): continue
                    # Pivot to real ticker if it's a known name alias (v22.30 Radar)
                    final_ticker = alias_map.get(c_up, c_up)
                    cands.add(final_ticker)
                for ticker, d in master_data.items():
                    name = (d.get("name") or d.get("research", {}).get("company") or "").lower()
                    if name and len(name) > 3 and name in text.lower():
                        cands.add(ticker.upper())
            return cands

        candidates = extract_candidates(all_src)
        for stories in news_db.values():
            candidates.update(extract_candidates(stories))
        
        # Final pass discovery with 15M TTL check (V22.9)
        # V22.54: Integrated legitimacy check into missing-asset calculation
        missing = [t for t in candidates if self.is_legit_ticker(t) and not self.is_entity_fresh(t, prices)]
        
        if missing:
            stasis_count = len(candidates) - len(missing)
            if stasis_count > 0:
                print(f"[INTEL] Cache Hit: {stasis_count} assets flaired from memory (Weekend Stasis).")
            print(f"[INTEL] Cache Miss: {len(missing)} assets identified as New/Missing. Hydrating...")
            
            new_prices = self._fetch_ancillary_prices(missing, prices)
            prices.update(new_prices)
            # V22.17: Atomic Force-Save to ensure discovery is captured
            self._save_json("live_prices.json", prices)
        else:
            if candidates:
                print(f"[INTEL] Full Stasis: all {len(candidates)} assets flaired from cache.")
        
        # Reload entities now that prices is updated
        # 3. Prioritized Narrative Synthesis
        ticker_news = []
        for ticker, stories in news_db.items():
            entry = master_data.get(ticker, {})
            # V22.1 Logic: Prioritize High Alpha & Hidden Monitoring Plays
            alpha = float(entry.get("human_research", {}).get("Alpha Score", 0) or 0)
            hidden = float(entry.get("human_research", {}).get("Hiddenness Score", 0) or 0)
            priority = (alpha * 1.5) + (hidden * 0.8)
            
            for s in stories:
                try:
                    ts = s.get('date')
                    if isinstance(ts, int) or (isinstance(ts, str) and ts.isdigit()):
                        dt = datetime.datetime.fromtimestamp(int(ts))
                    else:
                        dt = datetime.datetime.fromisoformat(str(ts).replace("Z", "").split("+")[0])
                    if dt >= limit:
                        ticker_news.append({
                            "ticker": ticker, 
                            "title": s['title'], 
                            "summary": s.get('summary', ''),
                            "date": dt,
                            "priority": priority,
                            "link": s.get('link', '#')
                        })
                except: continue
        
        # V22.42: News quality blacklist
        NEWS_BLACKLIST = [
            ' morning update', ' summary', ' what to know', 'preview:', 'dave ramsey', 'david einhorn'
        ]
        def is_blacklisted(title):
            # Aggressive normalization for smart quotes and whitespace
            t_low = title.lower().replace('’', "'").replace('‘', "'")
            # V22.99: Strict Stablecoin news purge
            if any(sc.lower() in t_low for sc in ["usdc", "usdt", "tether", "stablecoin", "circle"]): return True
            return any(bl in t_low for bl in NEWS_BLACKLIST)

        # Sort by Alpha/Hiddenness Priority instead of just Date
        # V22.99: Use Rating Scale (Alpha) as primary weight
        ticker_news.sort(key=lambda x: (x['priority'], x['date']), reverse=True)
        # Apply blacklist filter to ticker-level news too
        ticker_news = [n for n in ticker_news if not is_blacklisted(n['title'])]

        # V22.95: Session-aware sentiment tracking
        total_p = 0; up_count = 0
        for sym, p in prices.items():
            _, pct, _ = self.get_session_data(p, sym)
            total_p += 1
            if pct > 0: up_count += 1
            
        risk_on = (up_count / total_p) > 0.5 if total_p > 0 else False
        sentiment_label = "RISK-ON // ACCUMULATING" if risk_on else "RISK-OFF // PROTECTING"

        macro_ps = []
        # V22.98: Data-Driven Market Pulse Narrative
        m_fg = int(sentiment.get('market', {}).get('value', 50))
        c_fg = int(sentiment.get('crypto', {}).get('value', 50))        # Determine Market Session Sentiment in words
        spx = prices.get('ES=F', prices.get('^GSPC', {}))
        _, spx_chg, _ = self.get_session_data(spx, "ES=F")
        
        vibe = "BULLISH" if spx_chg > 0.5 else "BEARISH" if spx_chg < -0.5 else "NEUTRAL / CHOPPY"
        # V23.01: Comprehensive Macro Intelligence Briefing
        pulse_text = (
            f"The session is carving out a <b>{vibe}</b> posture (F&G: {m_fg}). "
            f"Overall market sentiment is <b>{sentiment_label}</b> as liquidity shifts between defensive rotations and high-alpha sector accumulation. "
        )
        
        # Prepare Newsletter Synthesis (Top of Report)
        # V23.01: Aggressive filtering for Headlines first
        unique_h = set()
        used_for_headlines = set()
        SIGNALS = ["chip", "semi", "ai ", "data center", "nvidia", "intel", "amd", "infrastructure", "optics", "cpo", "lithography", "tsmc", "asml", "wafer", "foundry", "fab", "hbm", "cowos", "broadcom", "arm", "semiconductor"]
        
        # Sort macro by relevance first
        def get_macro_score(h):
            score = 0
            t = h['title'].lower()
            if any(s in t for s in SIGNALS): score += 75 # V23.49: Boosted Semi weight
            if any(symbol in t.upper() for symbol in master_data.keys()): score += 100
            if any(x in t for x in ["breakthrough", "monopoly", "subsidy", "choke", "fab ", "foundry"]): score += 40
            return score
            
        if macro_headlines:
            macro_headlines.sort(key=lambda x: (get_macro_score(x), x.get('date', 0)), reverse=True)
            
        headline_divs = []
        h_count = 0
        used_headline_icons = set()
        
        # V23.49: Consecutive Icon De-duplication logic
        available_macro = [h for h in macro_headlines if not is_blacklisted(h['title']) 
                          and h['title'] not in unique_h 
                          and all(x not in h['title'] for x in ["Yahoo", "Morning Update", "Summary", "What to Know"])]
        
        while h_count < 15 and available_macro:
            # V23.60: Find the highest scoring headline with a unique icon if possible
            best_idx = -1
            for i, h in enumerate(available_macro):
                # Peak at what icon it would get without adding it to used set yet
                icon = self.get_context_icon(h['title'], used_icons=None)
                if icon not in used_headline_icons:
                    best_idx = i
                    break
            
            # If we've exhausted all categories, fallback to first in list
            if best_idx == -1:
                best_idx = 0
            
            h = available_macro.pop(best_idx)
            title_low = h['title'].lower()
            if get_macro_score(h) < 10 and any(noise in title_low for noise in ["preview", "look at", "earn"]): continue
            
            # Now actually get and record the icon
            icon = self.get_context_icon(h['title'], used_icons=used_headline_icons)
            
            unique_h.add(h['title'])
            flaired_title = self.inject_price_flair(h['title'], prices, master_data)
            link = h.get('link', '#')
            
            headline_divs.append(f"<div style='margin-bottom:6px; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:5px;'><span style='color:#0ea5e9; font-size:11px; vertical-align:middle; margin-right:6px;'>{icon}</span> <a href=\"{link}\" style=\"color:#f8fafc; font-size:13px; font-weight:500; text-decoration:none;\">{flaired_title}</a></div>")
            used_for_headlines.add(h['title'])
            h_count += 1

        # V23.01: Generate the Comprehensive Narrative BEFORE the headlines
        synthesis_pool = [h for h in macro_headlines if h['title'] not in used_for_headlines and not is_blacklisted(h['title'])] + ticker_news[:30]
        # Request a deeper synthesis (20 sentences across paragraphs for higher fidelity)
        nlp_summary = nlp.synthesize_macro_overview(synthesis_pool, sentences_count=20, group_paragraphs=True)
        
        comp_narrative = []
        for p in nlp_summary:
            if isinstance(p, dict):
                html_items = []
                for item in p['items']:
                    flaired = self.inject_price_flair(item['text'], prices, master_data)
                    html_items.append(f"<li style='margin-bottom:8px;'><a href=\"{item['link']}\" style='color:#cbd5e1; text-decoration:none;\">{flaired}</a></li>")
                group_html = f"<div style='margin-bottom:24px;'><div style='color:#0ea5e9; font-weight:bold; font-size:12px; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;'>{p['transition']}</div><ul style='margin-top:0; padding-left:20px; font-size:14px; line-height:1.6;'>{''.join(html_items)}</ul></div>"
                comp_narrative.append(group_html)
            else:
                comp_narrative.append(self.inject_price_flair(p, prices, master_data))
        
        # Build the Macro HTML block
        report_blocks = []
        # Block 1: Executive Summary
        summary_html = f"<div style='background:rgba(21,128,61,0.05) if risk_on else rgba(245,158,11,0.05); padding:18px; border-radius:5px; border-left:4px solid {gold if not risk_on else '#10b981'}; margin-bottom:24px; color:#cbd5e1; font-size:15px; line-height:1.7;'><b>Executive Summary:</b> {pulse_text}</div>"
        report_blocks.append(summary_html)
        
        # Block 2: Comprehensive Intelligence Briefing (The Narrative)
        for p in comp_narrative:
            if p.startswith("<div"):
                report_blocks.append(p)
            else:
                report_blocks.append(f"<p style='color:#cbd5e1; line-height:1.8; font-size:14px; margin-bottom:20px;'>{p}</p>")
            
        # Block 3: Institutional Pulse (Top 15 Headlines)
        if headline_divs:
            report_blocks.append(f'<div class="section-hdr" style="color:{text_dim}; font-family:monospace; font-size:9px; letter-spacing:2px; text-transform:uppercase; font-weight:bold; margin-top:30px; margin-bottom:15px;">Institutional Pulse // Headlines (Top 15)</div>')
            report_blocks.extend(headline_divs)
        
        macro_ps = report_blocks
        
        # V23.60: Premium Velocity Override construction
        m_candidates = []
        for k, v in prices.items():
            if not self.is_legit_ticker(k) or self.is_shite_ticker(k): continue
            
            p_val, p_pct, p_sess = self.get_session_data(v, k)
            if p_pct is None or abs(p_pct) < 0.1: continue 
            
            vol = v.get("vol_spike") if v.get("vol_spike") is not None else 1.0
            if vol < 1.2: continue # 20% vol surge minimum
            
            m_candidates.append({"s": k, "v": abs(p_pct) * vol, "pct": p_pct, "vol": vol})

        momentum_top = sorted(m_candidates, key=lambda x: x['v'], reverse=True)[:6]
        if momentum_top:
            mv_rows = []
            for m in momentum_top:
                pct = m['pct']
                vol = m['vol']
                # CSS Bar for Email: Faked with non-breaking spaces and background color
                # vol_scaled = min(100, int((vol/5)*100))
                # using a table-based visual bar for higher compatibility
                bar_width = min(60, int(vol * 15))
                bar_html = f'<span style="display:inline-block; background:#0ea5e9; height:2px; width:{bar_width}px; vertical-align:middle; margin-left:10px; border-radius:1px;"></span>'
                
                flaired = self.get_ticker_chip(m['s'], prices, simple=True, link=False)
                mv_rows.append(
                    f'<div class="mv-row" style="background:rgba(14,165,233,0.08); border-left:4px solid #0ea5e9; '
                    f'border-radius:4px; padding:10px 16px; margin-bottom:5px; '
                    f'font-family:monospace; font-size:13px; white-space:nowrap; overflow:hidden;">'
                    f'<span style="display:inline-block; min-width:130px;">{flaired}</span>'
                    f'<span class="mv-vol" style="color:#38bdf8; font-size:11px; margin-left:12px; font-weight:bold;">VOL ×{vol:.1f}</span>'
                    f'{bar_html}'
                    f'</div>'
                )
            report_blocks.append(
                f'<div style="margin:20px 0 30px 0;">'
                f'<div class="section-hdr" style="color:#0ea5e9; font-family:sans-serif; font-size:10px; letter-spacing:3px; '
                f'text-transform:uppercase; font-weight:900; margin-bottom:12px; padding-bottom:6px; '
                f'border-bottom:2px solid rgba(14,165,233,0.3);">Velocity Override // Vol Spikes</div>'
                f'{"".join(mv_rows)}</div>'
            )

        macro_ps = report_blocks

        sector_ps = []
        seen_titles = set()
        count = 0
        for news in ticker_news:
            if count >= 8: break # Expanded to Top 8 for broader sector visibility
            if news['title'] not in seen_titles:
                # Pulse links also get flair
                flaired_title = self.inject_price_flair(news['title'], prices, master_data)
                sector_ps.append(f"<b>{self.get_ticker_chip(news['ticker'], prices)} Catalyst:</b> <span style=\"color:#f8fafc;\">{flaired_title}</span>")
                seen_titles.add(news['title'])
                count += 1
                
        sector_ps.append("<br><b style='color:#f59e0b; font-size:12px;'>--- SOVEREIGN SECTOR DOSSIER ---</b>")
        # Themes and summary now reflect prioritized top-tier plays
        nlp_themes = nlp.get_top_themes(ticker_news[:20], top_n=6)
        if nlp_themes:
            # Themes get flair lookup
            flaired_themes = [self.inject_price_flair(t, prices, master_data) for t in nlp_themes]
            sector_ps.append(f"<div style='color:#94a3b8; margin:10px 0;'><b>Active Alpha Themes:</b> {', '.join(flaired_themes)}</div>")
            
        # V22.2: Detailed 3-4 Paragraph Sector Synthesis
        nlp_sector_summary = nlp.synthesize_macro_overview(ticker_news[:15], sentences_count=12, group_paragraphs=True)
        if nlp_sector_summary:
            for p in nlp_sector_summary:
                if isinstance(p, dict):
                    html_items = []
                    for item in p['items']:
                        flaired = self.inject_price_flair(item['text'], prices, master_data)
                        html_items.append(f"<li style='margin-bottom:8px;'><a href=\"{item['link']}\" style='color:#cbd5e1; text-decoration:none;'>{flaired}</a></li>")
                    group_html = f"<div style='margin-top:16px;'><div style='color:#0ea5e9; font-weight:bold; font-size:11px; margin-bottom:6px;'>{p['transition']}</div><ul style='margin-top:0; padding-left:20px; font-size:13px; line-height:1.6;'>{''.join(html_items)}</ul></div>"
                    sector_ps.append(group_html)
                else:
                    fr_p = self.inject_price_flair(p, prices, master_data)
                    sector_ps.append(f"<div style='color:#cbd5e1; margin-top:10px; line-height:1.6;'>{fr_p}</div>")

        return macro_ps, sector_ps, sentiment_label, watchlist_intel_html

    def gather_all_data(self, custom_tickers=None):
        print("[DEBUG] gather_all_data: Loading master/prices...")
        master = self._load_json("CPO_MASTER_DATA.json")
        prices = self._load_json("live_prices.json")
        print("[DEBUG] gather_all_data: Master/Prices loaded.")
        
        # Hot-fetch macro prices automatically so no manual sync is required
        macro_tickers = [
            'BTC-USD', 'ETH-USD', 'SOL-USD',  # Crypto 24/7
            '^GSPC', '^IXIC', '^DJI',          # US Cash Indices (Friday Close)
            'NQ=F', 'ES=F', 'YM=F',            # US Futures (Sunday Night Live)
            '^HSI', '^N225',                    # Asia (HK/Japan)
            '^GDAXI', '^FTSE',                  # Europe (Germany/UK)
            'CRCL',                             # Force-fetch: recently listed US stock
        ]
        is_active = self.is_market_active()
        
        # V22.33: Apply universal freshness pulse allowing missing prices to bypass stasis
        missing = []
        ts_map = prices.get("_meta", {}).get("timestamps", {})
        # V23.46: Merge custom CLI tickers into the high-frequency pulse loop
        high_priority = macro_tickers + (custom_tickers or [])
        for t in high_priority:
            is_stale = not self.is_entity_fresh(t, prices)
            ts = ts_map.get(t) or prices.get(t, {}).get('timestamp', 0)
            age = int(time.time() - ts) // 60 if ts > 0 else 0

            if is_stale:
                # If price is TOTALLY missing, we always fetch (The Data-Void Exception)
                has_no_price = t not in prices or prices[t].get('price') is None
                if has_no_price:
                    print(f"[CACHE] Missing: {t} - Fetching.")
                    missing.append(t)
                    continue
                    
                # V22.56: Futures awareness for Sunday Night (ES=F, NQ=F)
                if not is_active and "USD" not in t and "=F" not in t: 
                    print(f"[CACHE] Weekend Stasis: {t} ({age}m) - Skip.")
                    continue

                print(f"[CACHE] Stale: {t} ({age}m) - Fetching.")
                missing.append(t)
            else:
                print(f"[CACHE] Fresh: {t} ({age}m) - Skip.")
                
        if missing:
            try:
                # V22.16: Macro persistence enabled to ensure Friday close is anchored
                new_prices = asyncio.run(async_run_fetch(tickers=missing, dry_run=False, skip_sync=False))
                
                # V22.56: PRESERVE TIMESTAMPS. Merge meta to avoid cache-wiping.
                if "_meta" in new_prices:
                    if "_meta" not in prices: prices["_meta"] = {"timestamps": {}}
                    prices["_meta"].setdefault("timestamps", {}).update(new_prices["_meta"].get("timestamps", {}))
                
                for k, v in new_prices.items():
                    if k != "_meta" and v.get("change_pct") is not None:
                        prices[k] = v
                # V22.17: Force-Save macro update
                self._save_json("live_prices.json", prices)
            except Exception as e:
                print(f"[ERR] Live fetch failed: {e}")

        news_db = self._load_json("YAHOO_NEWS_DB.json").get("news", {})
        sentiment = self.fetch_sentiment()
        tradeable = {"semi": [], "ai": []}; strategic = []
        universe = set(master.keys())
        custom_set = set([t.upper() for t in custom_tickers]) if custom_tickers else set()
        universe.update(custom_set)

        if self.web_root.exists():
            for d in self.web_root.iterdir():
                if d.is_dir() and (d / "dashboard_data.js").exists():
                    try:
                        with open(d / "dashboard_data.js", "r", encoding="utf-8") as f:
                            universe.update(re.findall(r'"([A-Z0-9\.]+)"\s*:', f.read()))
                    except: continue

        # Data-Void sector hydration: fetch any tracked stock with no price in cache
        sector_void = []
        for sym in universe:
            # Map common crypto aliases
            if sym == "ADA": sym = "ADA-USD"
            
            entry = master.get(sym, {}).get("human_research", {})
            # Skip hydration for Private/Acquired assets
            if entry.get("Bucket") in ["Private", "Pre-IPO"]: continue
            if "acquired" in entry.get("Notes", "").lower(): continue
            if not self.is_legit_ticker(sym): continue
            
            # V23.46: Hydrate if missing OR stale (STALE ONLY IF MARKET ACTIVE/CRYPTO)
            is_stale = not self.is_entity_fresh(sym, prices)
            has_no_price = sym not in prices or prices[sym].get('price') is None
            
            if has_no_price or is_stale:
                sector_void.append(sym)
        if sector_void:
            print(f"[INTEL] Sector Data-Void: {len(sector_void)} assets need hydration. Fetching...")
            try:
                chunk_size = 20
                for i in range(0, len(sector_void), chunk_size):
                    chunk = sector_void[i:i+chunk_size]
                    sv_prices = asyncio.run(async_run_fetch(tickers=chunk, dry_run=False, skip_sync=True))
                    for k, v in sv_prices.items():
                        if k != "_meta" and v.get("price") and v['price'] > 0:
                            prices[k] = v
                self._save_json("live_prices.json", prices)
            except Exception as e:
                print(f"[WARN] Sector hydration partial: {e}")

        tradeable = {"semi": [], "ai": [], "watchlist": []}; strategic = []
        for sym in universe:
            entry = master.get(sym, {"human_research": {"Ticker": sym, "Company": sym}})
            res = entry.get("human_research", {}); p_data = prices.get(sym, {}); notes = res.get("Notes", "")
            
            # V22.95: High-Fidelity Session Awareness
            price, pct, sess = self.get_session_data(p_data, sym)
            
            item = {
                "symbol": sym, 
                "name": res.get("Company") or sym, 
                "pct": pct, 
                "notes": notes, 
                "alpha": float(res.get("Alpha Score", 0) or 0), 
                "role": (res.get("Role") or "").lower(),
                "priority": 100 if sym in custom_set else 0
            }
            if res.get("Bucket") in ["Private", "Pre-IPO"] or "acquired" in notes.lower():
                strategic.append(item); continue
            
            if sym in custom_set:
                tradeable["watchlist"].append(item)
            elif "semi" in item["role"] or "chip" in item["role"]: 
                tradeable["semi"].append(item)
            else: 
                tradeable["ai"].append(item)

        tradeable["watchlist"].sort(key=lambda x: x['pct'], reverse=True)
        tradeable["ai"].sort(key=lambda x: (x['alpha'], abs(x['pct'])), reverse=True)
        tradeable["semi"].sort(key=lambda x: (x['alpha'], abs(x['pct'])), reverse=True)
        tradeable["semi"] = tradeable["semi"][:15]; tradeable["ai"] = tradeable["ai"][:15]
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
        session = "WEEKEND INTEL" if self.now.weekday() >= 5 else "MARKET LIVE"
        
        # Sentiment Calculations
        market_fg = int(sentiment.get('market', {}).get('value', 50))
        crypto_fg = int(sentiment.get('crypto', {}).get('value', 50))
        
        def get_fg_color(v):
            if v <= 25: return bear # Extreme Fear
            if v <= 45: return "#ff9f1c" # Fear
            if v <= 55: return text_dim # Neutral
            if v <= 75: return bull # Greed
            return "#6ee7b7" # Extreme Greed (site green-300)

        m_color = get_fg_color(market_fg)
        c_color = get_fg_color(crypto_fg)

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

        if is_live_main:
            index_tiles = []
            for index in COMPARATIVE_INDICES:
                c_data = prices.get(index['cash'], {})
                c_val, c_chg, _ = self.get_session_data(c_data, index['cash'])
                c_color = bull if c_chg >= 0 else bear
                index_tiles.append(render_tile(index['cash'], index['name'], c_val, c_chg, "LIVE", c_color))
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
                perf_candidates.append({'s': sym, 'p': price, 'pct': pct, 'sess': sess})
        
        # Gainers: Greatest to Least
        gainers_top = sorted([p for p in perf_candidates if p['pct'] > 0], key=lambda x: x['pct'], reverse=True)[:10]
        # Losers: Most Negative to Least Negative
        losers_top = sorted([p for p in perf_candidates if p['pct'] < 0], key=lambda x: x['pct'])[:10]

        def render_perf_list(items, color, align="center"):
            rows = []
            for item in items:
                sess_tag = self.get_session_tag_html(fs="9px", sess_override=item['sess'])
                # High-fidelity: reduced padding, improved font weight, absolute-minimum margins
                rows.append(
                    f'<div class="perf-item" style="font-family:monospace; font-size:12px; margin-bottom:1px; line-height:1; '
                    f'background:rgba(255,255,255,0.03); border-radius:2px; padding:5px 8px; display:inline-block; width:100%; box-sizing:border-box; text-align:left; border-bottom:1px solid rgba(255,255,255,0.02);">'
                    f'<span style="color:{gold}; font-weight:bold; display:inline-block; width:70px;">${item["s"]}</span> '
                    f'<span style="color:{color}; font-weight:900; margin-left:6px; font-size:13px;">{item["pct"]:+.2f}%</span>'
                    f'<span style="float:right; margin-top:0px;">{sess_tag}</span>'
                    f'</div>'
                )
            return "".join(rows) if rows else '<div style="color:#4a5568; font-size:11px; padding:15px 0; text-align:center;">None identified</div>'

        # V23.60: Tightened Centered Overhaul for Desktop Display
        perf_carveout_html = f"""
        <tr><td style="padding:15px 0 25px 0;">
            <div class="section-hdr" style="font-family:monospace; font-size:11px; letter-spacing:5px; text-transform:uppercase; font-weight:bold; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.1); text-align:center; color:{text_bright};">Session Performance // Top 10 Movers</div>
            <table width="100%" cellpadding="0" cellspacing="0"><tr>
                <td class="perf-cell" width="50%" style="vertical-align:top; border-right:1px solid rgba(255,255,255,0.08); padding:0 8px; text-align:center;">
                    <div class="perf-hdr" style="color:{bull}; font-size:11px; font-weight:900; margin-bottom:8px; text-transform:uppercase; letter-spacing:2px;">▲ Top Gainers</div>
                    <div style="display:inline-block; text-align:left; width:100%;">{render_perf_list(gainers_top, bull, align="center")}</div>
                </td>
                <td class="perf-cell" width="50%" style="vertical-align:top; padding:0 8px; text-align:center;">
                    <div class="perf-hdr" style="color:{bear}; font-size:11px; font-weight:900; margin-bottom:8px; text-transform:uppercase; letter-spacing:2px;">▼ Top Losers</div>
                    <div style="display:inline-block; text-align:left; width:100%;">{render_perf_list(losers_top, bear, align="center")}</div>
                </td>
            </tr></table>
        </td></tr>
        """

        # 3. Narrative Intelligence
        macro_ps, sector_ps, sentiment_label, watchlist_intel_html = self.synthesize_dossier(news_db, prices, master, sentiment)
        macro_html = "".join([
            f'<div style="color:{text_dim}; font-size:15px; line-height:1.7; margin-bottom:14px; white-space:normal !important; overflow:visible !important;">'
            f'{p}</div>' for p in macro_ps
        ])

        # V23.60: Sector Dossier Cards — N/A guard for missing prices
        def render_bucket(title, items, hide_notes=False):
            if not items: return ""
            rows = []
            for t in items:
                sym = t.get('symbol', '').replace('$', '')
                p_entry = prices.get(t['symbol'], {})
                price, pct, sess = self.get_session_data(p_entry, t['symbol'])
                has_price = price and price > 0
                
                if not has_price:
                    pct_display = '<span style="color:#4a5568; font-size:10px;">N/A</span>'
                    clr = text_dim
                else:
                    clr = bull if pct >= 0 else bear
                    sess_tag = self.get_session_tag_html(fs="9px", sess_override=sess)
                    price_str = f'<span class="sec-price" style="color:#cbd5e1; font-size:10px; margin-right:8px;">${price:,.2f}</span>'
                    pct_display = f'{price_str}<span class="sec-pct-val" style="color:{clr}; font-weight:bold;">{pct:+.2f}%{sess_tag}</span>'

                notes = "" if hide_notes else t.get('notes', '').strip()
                # HARDENED: Inject price flair without clickable blue links for notes
                flaired_notes = self.inject_price_flair(notes, prices, link=False)
                
                # Check if name is redundant with symbol
                display_name = t['name']
                if display_name.upper() == sym.upper():
                    # If name is same as ticker, try to fetch from name map or just hide it
                    display_name = self.ticker_name_map.get(sym, "")
                    if not display_name or display_name.upper() == sym.upper():
                        display_name = ""

                rows.append(f"""
                    <div class="sector-card" style="background:{bg_accent}; border-left:2px solid {clr}; padding:8px 12px; border-radius:4px; margin-bottom:2px;">
                        <table width="100%" cellpadding="0" cellspacing="0"><tr>
                            <td class="sec-ticker" width="28%" style="font-family:monospace; font-weight:bold; font-size:13px; white-space:nowrap;"><a href="https://finance.yahoo.com/quote/{t['symbol']}" style="color:{gold}; text-decoration:none !important;">${t['symbol']}</a></td>
                            <td class="sec-name" width="30%" style="font-size:11px; color:{text_dim}; padding:0 8px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">{display_name}</td>
                            <td class="sec-pct" width="42%" style="text-align:right; font-family:monospace; font-size:13px;">{pct_display}</td>
                        </tr></table>
                        {f'<div class="sec-notes" style="font-size:10px; color:#8f9bb3; margin-top:4px; line-height:1.4; border-top:1px solid rgba(255,255,255,0.04); padding-top:4px; white-space:normal !important; word-wrap:break-word; overflow:visible !important; display:block;">{flaired_notes[:800]}</div>' if flaired_notes else ''}
                    </div>
                """)
            return (
                f'<div style="margin-top:12px;">'
                f'<div class="section-hdr" style="color:{text_dim}; font-family:monospace; font-size:9px; letter-spacing:3px; text-transform:uppercase; font-weight:bold; margin-bottom:6px; padding-bottom:4px; border-bottom:1px solid #1e2130;">— {title} —</div>'
                f'{"".join(rows)}'
                f'</div>'
            )

        watchlist_html = render_bucket("Real-time Watchlist // CLI Intel", tradeable.get("watchlist", []), hide_notes=True)
        semi_html = render_bucket("Sector Sentiment", tradeable.get("semi", []))
        ai_html = render_bucket("Algorithmic Intelligence", tradeable.get("ai", []))

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
                    .perf-cell {{ padding:0 20px !important; }}
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
                /* Mobile lock --- section-hdr stays small and dim */
                @media only screen and (max-width:599px) {{
                    .section-hdr {{
                        font-size:10px !important;
                        font-weight:bold !important;
                        color:{text_dim} !important;
                        letter-spacing:2px !important;
                    }}
                    /* Comparative Pulse Mobile centering and sizing */
                    .pulse-idx-name {{ font-size:11px !important; }}
                    .pulse-sub-label {{ font-size:8px !important; }}
                    .pulse-val {{ font-size:16px !important; }}
                    .pulse-chg {{ font-size:11px !important; }}
                    /* Crypto Mobile sizing */
                    .crypto-label {{ font-size:10px !important; }}
                    .crypto-val   {{ font-size:14px !important; }}
                    .crypto-chg   {{ font-size:11px !important; }}
                    .perf-item    {{ font-size:13px !important; }}
                    .perf-cell    {{ padding:0 8px !important; }}
                }}
            </style>
        </head>
        <body>
        <div class="wrap">
        <center>
        <table class="main-table" border="0" cellspacing="0" cellpadding="0" style="text-align:left; font-family:'Helvetica Neue',Arial,sans-serif;">

            <!-- ═══ HEADER ═══ -->
            <tr><td style="padding-bottom:24px;">
                <table width="100%" cellpadding="0" cellspacing="0"><tr>
                    <td class="header-cell">
                        <div class="header-title hdr-title" style="color:{text_bright}; font-size:16px; font-weight:bold; letter-spacing:1.5px; text-transform:uppercase;">Market Insights and Intel</div>
                        <div style="color:{text_dim}; font-size:10px; font-family:monospace; margin-top:3px; letter-spacing:0.5px;">V23.55 // {self.now.strftime('%a %Y-%m-%d %H:%M EST')} // {session}</div>
                    </td>
                    <td class="badge-cell" style="text-align:right; white-space:nowrap; vertical-align:middle; padding-left:10px;">
                        <span style="background:{accent}; color:#fff; padding:4px 10px; font-size:9px; border-radius:2px; font-weight:bold; letter-spacing:1px;">CONFIDENCE: HIGH</span>
                    </td>
                </tr></table>
            </td></tr>

            <!-- ═══ PULSE BLOCK ═══ -->
            <tr><td class="narrative-box" style="background:{bg_surface}; padding:20px; border-radius:6px;">

                <!-- US Markets grid -->
                <div class="section-hdr" style="font-size:9px; font-family:monospace; color:{gold}; letter-spacing:2px; text-transform:uppercase; font-weight:bold; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid rgba(245,158,11,0.2);">Sovereign Index Pulse // Divergence</div>
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;">
                    {pulse_grid_rows}
                    {crypto_pulse_row}
                </table>

                <!-- Global Markets grid -->
                <div class="section-hdr" style="font-size:9px; font-family:monospace; color:{text_dim}; letter-spacing:2px; text-transform:uppercase; font-weight:bold; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid {border};">Global Markets</div>
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;">{global_grid_rows}</table>

                {perf_carveout_html}
                
                <!-- WATCHLIST INTEL -->
                {watchlist_intel_html}

                <!-- Fear & Greed — centered 2-col -->
                <div class="section-hdr" style="font-size:9px; font-family:monospace; color:{text_dim}; letter-spacing:2px; text-transform:uppercase; font-weight:bold; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid {border};">Sentiment</div>
                <table width="100%" cellpadding="0" cellspacing="0"><tr>
                    <td width="50%" style="padding:3px; vertical-align:top;">
                        <div style="background:{bg_deep}; border-radius:5px; padding:12px 8px; text-align:center;">
                            <div class="fg-label" style="font-size:8px; font-family:monospace; color:{text_dim}; letter-spacing:1px; margin-bottom:4px;">MARKET F&amp;G</div>
                            <div class="fg-val" style="font-size:22px; font-weight:bold; color:{m_color}; line-height:1;">{market_fg}</div>
                            <div style="font-size:7px; color:{text_dim}; margin-top:3px;">FEAR &amp; GREED</div>
                        </div>
                    </td>
                    <td width="50%" style="padding:3px; vertical-align:top;">
                        <div style="background:{bg_deep}; border-radius:5px; padding:12px 8px; text-align:center;">
                            <div class="fg-label" style="font-size:8px; font-family:monospace; color:{text_dim}; letter-spacing:1px; margin-bottom:4px;">CRYPTO F&amp;G</div>
                            <div class="fg-val" style="font-size:22px; font-weight:bold; color:{c_color}; line-height:1;">{crypto_fg}</div>
                            <div style="font-size:7px; color:{text_dim}; margin-top:3px;">COIN GLASS</div>
                        </div>
                    </td>
                </tr></table>
            </td></tr>

                <!-- Narrative Intel -->
                <tr><td style="padding-bottom:30px;">
                    <div style="border-left:3px solid {gold}; padding-left:20px; margin-bottom:30px;">
                        <div class="section-hdr macro-hdr" style="color:{gold}; font-family:sans-serif; font-size:12px; font-weight:bold; margin-bottom:15px;">I. MACRO // GLOBAL PULSE</div>
                        {macro_html}
                    </div>
                    {watchlist_html}
                    {semi_html}
                    {ai_html}
                </td></tr>

                <!-- Footer -->
                <tr><td style="padding:30px 0; border-top:1px solid #25272d; text-align:center;">
                    <div style="color:{text_dim}; font-size:10px; font-family:monospace;">
                        END OF DOSSIER // TRANSMISSION SECURE // {session}<br>
                        SOVEREIGN ENGINE HARDENED // AUTO-GENERATED BY GIGACPO V23.49
                    </div>
                </td></tr>
            </table>
            </center>
        </body></html>
        """
        return html

    def send_email(self, html):
        u = os.getenv("GMAIL_USER")
        pk = os.getenv("GMAIL_APP_PASS")
        r = os.getenv("RECIPIENT_EMAIL", "rayjonesy@gmail.com")
        display_name = os.getenv("GMAIL_DISPLAY_NAME", "Market News")
        
        salt = uuid.uuid4().hex[:8]
        msg = MIMEMultipart()
        msg['From'] = f"{display_name} <{u}>"
        msg['To'] = r
        msg['Subject'] = f"Market Insights and Sovereign Intel // {self.now.strftime('%m/%d/%y')} [{salt}]"
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

    def ts(): return datetime.datetime.now().strftime("%H:%M:%S")

    print(f"[{ts()}] [DEBUG] Initializing SovereignIntelligenceEngine...")
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
    
    preview_path = engine.db_path / "synopsis_preview.html"
    with open(preview_path, "w", encoding="utf-8") as f: 
        f.write(html)
    
    if args.test_email:
        engine.send_email(html)
    else:
        print(f"Dossier generated: {preview_path}")
