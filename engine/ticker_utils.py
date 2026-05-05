"""
engine/ticker_utils.py
======================
The Single Source of Truth for ticker discovery across the GIGACPO ecosystem.
Unifies Root, AI, and Macro indices into a single monitored universe.
"""

VERSION = "V30.6.10"

# V23.59: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
except ImportError:
    pass

import datetime
import json
import time
import urllib.parse
from pathlib import Path

try:
    from market_session import MarketSession
except ImportError:
    from engine.market_session import MarketSession

ROOT = Path(__file__).parent.parent
CPO_DB = ROOT / "database" / "CPO_MASTER_DATA.json"
AI_DB = ROOT / "database" / "AI_MASTER_DATA.json"

# Global Skip List: Private or non-tradable entities, and common technical false positives
SKIP_TICKERS = {
    "CD",
    "AYAR",
    "RANV",
    "CelestialAI",
    "SCINTIL",
    "PHOTONIC_COMPUTING",
    "OPTICAL_INTERCONNECT",
    "SEMICON",
    "800G",
    "1.6T",
    "3.2T",
    "5B",
    "2026-2028",
    "OFC",
    "CIOE",
    "INNO",
    "IPH",
    "LITT",
    "LR4",
    "DR8",
    "FR4",
    "400G",
    "PAM4",
    "2027",
    "2.63B",
    "RITTAL",
    "SUBMER",
    "KINSUS",
    "ECTC",
    "NEG",
    "KCC",
}

# Common company names to Yahoo symbols
TICKER_MAPPING = {
    "SHINKO": "6967.T",
    "IBIDEN": "4062.T",
    "UNIMICRON": "3037.TW",
    "KINSUS": "3189.TW",
    "SIVE": "SIVE.ST",
    "SIVEF": "SIVE.ST",
    "IQEPF": "IQE.L",
    "FERRF": "6890.T",
    "0522.HK": "0522.HK",
    "ASMVY": "ASMVY",
    "PVS.DE": "PSM.DE",  # ProSiebenSat.1
}

# Global Macro Indices & Crypto
GLOBAL_INDICES = ["BTC-USD", "ETH-USD", "NQ=F", "ES=F", "YM=F"]

# V30.4.9: Authoritative Semiconductor Intelligence Tokens
SEMI_SOURCES = [
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
    "Semi Today Markets",
    "Semi Today Suppliers",
    "Semi Today Opto",
    "Semi Today Micro",
    "Semi Packaging News",
    "Yahoo Semi",
]

SEMI_KEYWORDS = [
    "CHIPLET",
    "TAPE-OUT",
    "PHOTONICS",
    "EDA TOOL",
    "WAFER",
    "LITHOGRAPHY",
    "FAB ",
    "ASIC",
    "FPGA",
    "GPU CLUSTER",
    "HBM3",
    "TSV",
    "HYBRID BONDING",
    "N3P",
    "N2 ",
    "1.4NM",
]

MAJOR_SEMI_TICKERS = [
    "NVIDIA",
    "INTEL",
    "AMD",
    "TSMC",
    "ASML",
    "ARM",
    "BROADCOM",
    "MU ",
    "MICRON",
]

# V30.6.10: Authoritative Ticker Legitimacy Blacklist
# Prevents common words and prepositions (e.g. ON, AT, IF) from being misinterpreted as tickers.
TICKER_BLACKLIST = {
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
    "A",
    "THE",
    "FOR",
    "WITH",
}


def is_legit_ticker(t: str) -> bool:
    """V30.6.10: Global authority for ticker verification."""
    if not t or not isinstance(t, str):
        return False
    t = t.upper().replace("$", "")
    if len(t) < 2 or t.isdigit():
        return False
    # Standard character constraints
    if any(x in t for x in [" ", "/", "\\", "(", ")", ",", ":", "'", '"']):
        return False

    # 2-Letter Whitelist logic (inherited from email engine)
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
            "UP",
            "ON",
            "ST",
            "SQ",
            "PYPL",
            "UBER",
            "LYFT",
        }
        if t not in WHITELIST_2:
            return False

    return t not in TICKER_BLACKLIST


def resolve_ticker(symbol: str) -> str:
    """Resolves a shorthand or name to a valid Yahoo Finance ticker."""
    return TICKER_MAPPING.get(symbol.upper(), symbol.upper())


def get_display_symbol(symbol: str) -> str:
    """V30.4.11: Returns the authoritative display label for a ticker (e.g. 'SIVE.TO/$SIVEF')."""
    s_upper = symbol.upper().replace("$", "")
    if s_upper in ["SIVE.TO", "SIVEF"]:
        return "SIVE.TO/$SIVEF"
    return s_upper


def load_master_tickers(terminal_type="union") -> list[str]:
    """
    Loads tickers from master databases.
    'root'  -> CPO_MASTER_DATA.json
    'ai'    -> AI_MASTER_DATA.json
    'union' -> Both + Global Indices
    """
    tickers = []

    def extract_from_file(path):
        if not path.exists():
            return []
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return [
                t
                for t, e in data.items()
                if e.get("human_research", {}).get("Bucket") != "Private" and t not in SKIP_TICKERS
            ]
        except Exception:
            return []

    if terminal_type == "static":
        tickers.extend(extract_from_file(CPO_DB))
        tickers.extend(extract_from_file(AI_DB))

    elif terminal_type in ["root", "union"]:
        tickers.extend(extract_from_file(CPO_DB))

    if terminal_type in ["ai", "union"]:
        tickers.extend(extract_from_file(AI_DB))

    if terminal_type == "union":
        tickers.extend(GLOBAL_INDICES)

    # Remove duplicates and clean
    return list(set([t.strip() for t in tickers if t]))


def get_ticker_count_report():
    """Returns a string summary of the ticker universe."""
    root_count = len(load_master_tickers("root"))
    ai_count = len(load_master_tickers("ai"))
    union_count = len(load_master_tickers("union"))
    return f"Ticker Universe: {union_count} (Root: {root_count}, AI: {ai_count}, Indices: {len(GLOBAL_INDICES)})"


def extract_ticker_eps(master, master_key):
    """
    V30.4: Authoritative EPS Extraction Logic.
    Extracts FY1 and FY2 EPS estimates from the master data trend.
    """
    if not master_key:
        return None, None
    data = master.get(master_key, {})
    fin = data.get("financials", {})
    et = fin.get("earningsTrend", {})
    trend = et.get("trend", [])

    eps26, eps27 = None, None
    for t in trend:
        # V28.8: Dynamic period detection for 2026/2027
        if t.get("period") == "0y":
            eps26 = t.get("earningsEstimate", {}).get("avg", {}).get("raw")
        elif t.get("period") == "+1y":
            eps27 = t.get("earningsEstimate", {}).get("avg", {}).get("raw")

    return eps26, eps27


def get_session_badge_style(s_type):
    """
    V30.4: Authoritative Session Badge Styling.
    Returns (BadgeText, Color) for a given session type.
    """
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


def get_header_timestamp(dt=None):
    """V30.4.9: Authoritative Institutional Header Timestamp."""
    dt = dt or datetime.datetime.now()
    return dt.strftime("%Y-%m-%d // %H:%M")


def format_news_date(ts):
    """V30.4.10: Formats an epoch timestamp for news display (e.g. 'May 04')."""
    if not ts:
        return ""
    try:
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime("%b %d")
    except:
        return ""


def is_semi_article(res):
    """
    V30.4.9: Authoritative Semiconductor Technical Check.
    Determines if an article is technical semi-trade news based on:
    1. Aggregator 'is_semi' flag (Source-of-truth)
    2. Hardcoded specialized source matching
    3. Deep technical keyword matching (Chiplet, Tape-out, etc.)
    """
    feed_name = res.get("source", "")
    title = res.get("title", "").upper()

    # 1. Direct Aggregator Flag
    if res.get("is_semi"):
        return True

    # 2. Known Specialized Sources
    if feed_name in SEMI_SOURCES:
        return True

    # 3. Deep Technical Keywords (Excluding generic ones to prevent bleed)
    if any(kw in title for kw in SEMI_KEYWORDS):
        return True

    return False


def get_authoritative_prev_close(p_data):
    """
    V30.4.18: Resolves the absolute authoritative previous session close price.
    Calculates it from regularMarketPrice and regularMarketChange if prev_close is missing.
    """
    if not p_data:
        return None

    pc = p_data.get("prev_close")
    if pc:
        return pc

    # Fallback calculation: Today's Close / (1 + Today's % Change)
    cp = p_data.get("close_price")
    pct = p_data.get("change_pct")

    if cp and pct is not None:
        try:
            calc = cp / (1 + (pct / 100))
            return round(calc, 3)
        except ZeroDivisionError:
            return cp

    return cp


def get_ticker_session_data(p_data, symbol=None, ms=None):
    """
    V30.4.22: Unified Session Pricing Logic.
    Extracts the correct price, percentage change, and session label.
    """
    ms = ms or MarketSession()
    sess = ms.get_market_session_label(symbol)
    if sess == "CLOSED":
        sess = ""

    price = p_data.get("price", 0)
    pct = p_data.get("change_pct", 0)

    ext_type = p_data.get("ext_type")
    effective_sess = sess

    if ext_type and ext_type in ["OVN", "PRE", "POST", "AH"]:
        # Session Match Logic
        match = (
            (ext_type == sess)
            or (sess == "AH" and ext_type in ["POST", "AH"])
            or (sess == "PRE" and ext_type == "PRE")
            or (sess == "OVN" and ext_type in ["POST", "AH", "OVN"])
        )

        # OVN Fallback
        if not match and sess == "PRE" and ext_type == "OVN":
            match = True

        if match:
            e_p = p_data.get("ext_price")
            if e_p is not None:
                price = e_p
                prev = get_authoritative_prev_close(p_data)
                if prev:
                    pct = ((price / prev) - 1) * 100
                elif p_data.get("ext_pct") is not None:
                    pct = p_data.get("ext_pct")

                effective_sess = ext_type if ext_type != "POST" else "AH"
        elif sess == "LIVE":
            effective_sess = "LIVE"
        else:
            effective_sess = ""

    return price, pct, effective_sess


def render_valuation_row(p_data, m_data, sym):
    """V30.4.22: Authoritative Valuation Logic."""
    m_cap = p_data.get("market_cap") or m_data.get("financials", {}).get("marketCap")
    pe = p_data.get("pe") or m_data.get("financials", {}).get("trailingPE")

    # V30.6.10: Prefer pre-hydrated forward estimates from p_data before recalculating
    pe26 = p_data.get("pe26")
    pe27 = p_data.get("pe27")

    if not pe26 or not pe27:
        eps26, eps27 = extract_ticker_eps({sym: m_data}, sym)
        price = p_data.get("price") or 0
        if not pe26 and eps26 and price:
            pe26 = price / eps26
        if not pe27 and eps27 and price:
            pe27 = price / eps27

    # Cap logic
    def cap(v):
        return v if v and -500 <= v <= 1000 else None

    pe26, pe27 = cap(pe26), cap(pe27)

    parts = []
    if m_cap:
        if m_cap >= 1e12:
            cap_str = f"${m_cap/1e12:.2f}T"
        elif m_cap >= 1e9:
            cap_str = f"${m_cap/1e9:.1f}B"
        else:
            cap_str = f"${m_cap/1e6:.1f}M"
        parts.append(f"MCap: {cap_str}")

    if pe26:
        parts.append(f"'26 [{pe26:.1f}]")
    if pe27:
        parts.append(f"'27 [{pe27:.1f}]")
    elif pe:
        parts.append(f"P/E: {pe:.1f}x")

    return parts
