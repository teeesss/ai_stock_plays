import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# GIGACPO Glass Substrate (LIDE/TGV) Intelligence
# V1.0 - Supply Chain Mapping
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
LOG_DIR = ROOT / "logs"
DB_PATH = ROOT / "database" / "CPO_MASTER_DATA.json"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "glass_intel.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("glass_intel")

# The "Definitive" Supply Chain Nodes identified via Research
GLASS_NODES = {
    "LPKF": {
        "ticker": "LPK.DE",
        "role": "LIDE Technology Provider (Critical Patent Holder)",
        "tech": ["Laser Induced Deep Etching", "TGV Hole Formation"],
        "partners": ["Intel", "Corning"],
        "sentiment": "S-Tier Technology",
    },
    "SKC / Absolics": {
        "ticker": "011790.KS",
        "role": "Glass Core Substrate Manufacturer",
        "tech": ["High-Volume Manufacturing (Georgia Factory)"],
        "partners": ["Applied Materials", "Samsung"],
        "sentiment": "Leading Commercial Execution",
    },
    "Corning": {
        "ticker": "GLW",
        "role": "Specialty Glass Material Producer",
        "tech": ["Fusion Forming Precision Glass"],
        "partners": ["LPKF", "Intel"],
        "sentiment": "Dominant Material Supplier",
    },
    "Samsung Electro-Mechanics": {
        "ticker": "009150.KS",
        "role": "Fabricator / System Integrator",
        "tech": ["Glass Substrate Pilot Line", "HBM4 Interposer Development"],
        "partners": ["NVIDIA", "SK Hynix"],
        "sentiment": "Heavy R&D Bias",
    },
    "Applied Materials": {
        "ticker": "AMAT",
        "role": "Equipment Supplier / Strategic Venture",
        "tech": ["Deposition & Etching Systems"],
        "partners": ["Absolics"],
        "sentiment": "Ecosystem Enabler",
    },
    "Besi": {
        "ticker": "BESIY",
        "role": "Advanced Packaging / Back-end Equipment",
        "tech": ["Hybrid Bonding", "Die Attach for HBM4/Glass"],
        "partners": ["TSMC", "Intel"],
        "sentiment": "Critical Bottleneck Supplier",
    },
    "ASM Pacific": {
        "ticker": "ASMVY",
        "role": "Thermal Compression Bonding",
        "tech": ["TCB for HBM", "Advanced Packaging"],
        "partners": ["SK Hynix", "Micron"],
        "sentiment": "High Volume Memory Packaging",
    },
}


def analyze():
    log.info("Starting Glass Substrate (LIDE/TGV) Intelligence mapping...")

    if not DB_PATH.exists():
        log.error("CPO_MASTER_DATA.json not found.")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        master = json.load(f)

    # Cross-reference existing master data with Glass Nodes
    updates = 0
    for node_name, info in GLASS_NODES.items():
        ticker = info["ticker"]
        # Find entry in master data (exact or contains)
        found_key = None
        for k in master.keys():
            if ticker.lower() in k.lower():
                found_key = k
                break

        if found_key:
            log.info(f"  ? Integrating Glass Intel into ${found_key}")
            if "human_research" not in master[found_key]:
                master[found_key]["human_research"] = {}

            master[found_key]["human_research"]["glass_substrate_v16"] = {
                "node_type": info["role"],
                "tech_stack": info["tech"],
                "key_partners": info["partners"],
                "sentiment": info["sentiment"],
                "market_narrative": "LIDE/TGV supercycle for AI/HBM4 packaging",
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            updates += 1
        else:
            log.warning(
                f"  [WARN] Node {node_name} (${ticker}) not found in master DB. High conviction play missing."
            )

    if updates > 0:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(master, f, indent=4, ensure_ascii=True)
        log.info(f"Saved glass intelligence to {DB_PATH}")


if __name__ == "__main__":
    analyze()
