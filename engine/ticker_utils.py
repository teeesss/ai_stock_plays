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

# Global Skip List: Private or non-tradable entities
SKIP_TICKERS = {
    "CD",
    "AYAR",
    "RANV",
    "CelestialAI",
    "SCINTIL",
    "PHOTONIC_COMPUTING",
    "OPTICAL_INTERCONNECT",
}

# Global Macro Indices & Crypto
GLOBAL_INDICES = ["BTC-USD", "ETH-USD", "NQ=F", "ES=F", "YM=F"]


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
