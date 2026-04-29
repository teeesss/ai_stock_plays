"""
engine/ticker_utils.py
======================
The Single Source of Truth for ticker discovery across the GIGACPO ecosystem.
Unifies Root, AI, and Macro indices into a single monitored universe.
"""

# V23.59: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
except ImportError:
    pass

import json
from pathlib import Path

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
    "0522.HK": "0522.HK",
    "ASMVY": "ASMVY",
    "PVS.DE": "PSM.DE",  # ProSiebenSat.1
}

# Global Macro Indices & Crypto
GLOBAL_INDICES = ["BTC-USD", "ETH-USD", "NQ=F", "ES=F", "YM=F"]


def resolve_ticker(symbol: str) -> str:
    """Resolves a shorthand or name to a valid Yahoo Finance ticker."""
    return TICKER_MAPPING.get(symbol.upper(), symbol.upper())


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
