"""
CPO Ecosystem Research Enrichment Engine
Uses curated research from Serenity (@aleabitoreddit), Perplexity, and Gemini
to fill TBD gaps, boost scores, add new stocks, and reclassify plays.

No external API calls required - pure research-driven enrichment.
"""

import csv

CSV_PATH = "cpo_master_ultimate.csv"

# ============================================================
# MASTER RESEARCH DATABASE
# Source: Serenity @aleabitoreddit, Perplexity deep dive, Gemini analysis
# ============================================================
ENRICHMENTS = {
    # === SERENITY HIGH-CONVICTION PICKS (proven 2x-5x performers) ===
    "AAOI": {
        "Alpha Score": "10",
        "Risk Adj": "5",
        "Target Upside": "5x",
        "Bucket": "Moonshot",
        "Rev Growth Est": "119% (1.6T AI pivot)",
        "Monopoly Score": "25% (800G/1.6T Modules)",
        "Notes": "5x YTD per Serenity. 119% sales growth. Pivoting to 1.6T hyperscale transceivers. Direct NVDA ecosystem beneficiary.",
    },
    "AXTI": {
        "Alpha Score": "10",
        "Target Upside": "5x",
        "Rev Growth Est": "200% (InP substrate shortage)",
        "Monopoly Score": "40% (InP/GaAs Oligopoly)",
        "Notes": "5x+ YTD per Serenity. Only US-listed InP substrate pure-play. 70% supply gap expected 2025-2026.",
    },
    "SIVE": {
        "Alpha Score": "9",
        "Target Upside": "5x",
        "Bucket": "Alpha",
        "Rev Growth Est": "100%+ (InP foundry ramp)",
        "Monopoly Score": "Independent InP Fab",
        "Notes": "2x+ YTD. Last independent InP foundry (Glasgow). Light source for JBL/MRVL. CHIPS Act $11.6M. Trades at 1/4 LWLG valuation.",
    },
    "AEHR": {
        "Alpha Score": "8",
        "Target Upside": "3x",
        "Bucket": "Alpha",
        "Rev Growth Est": "40% (SiPh burn-in pivot)",
        "Monopoly Score": "60% (Wafer-level burn-in)",
        "Notes": "2x+ YTD. Pivoting from SiC to SiPh testing. 100% wafer-level burn-in becoming mandatory for CPO.",
    },
    "TSEM": {
        "Alpha Score": "10",
        "Target Upside": "3x",
        "Rev Growth Est": "25% (SiPh foundry ramp)",
        "Monopoly Score": "40% (SiPh Foundry)",
        "Notes": "Near triple-digit returns YTD. TSM of photonics. Custom PDKs for CPO designers. Direct COHR/LITE foundry partner.",
    },
    "IQE": {
        "Alpha Score": "9",
        "Target Upside": "3x",
        "Bucket": "Alpha",
        "Rev Growth Est": "30% (Epi demand 2026)",
        "Monopoly Score": "40% (Global Epi)",
        "Notes": "2x+ YTD. Point72 aggressively buying. Critical InP/GaAs epiwafer supplier. Stronger demand visibility into 2026.",
    },
    "SOI": {
        "Alpha Score": "9",
        "Target Upside": "3x",
        "Rev Growth Est": "15% (Substrate recovery)",
        "Monopoly Score": "80% (FD-SOI Substrates)",
        "Notes": "Pure upstream bottleneck. Serenity favorite. Recovery from lows. AI/photonics angle underpriced by market.",
    },
    # === TIER 3/4 DEEP SUPPLY CHAIN (from Gemini/Perplexity research) ===
    "VECO": {
        "Alpha Score": "9",
        "Target Upside": "3x",
        "Rev Growth Est": "20% (InP MOCVD backlog)",
        "Monopoly Score": "50% (MOCVD Duopoly w/AIXA)",
        "Notes": "Virtual duopoly on InP MOCVD tools. Legacy LED stigma suppresses multiple. Compound semi backlog exploding.",
    },
    "AIXNY": {
        "Alpha Score": "9",
        "Target Upside": "1x-2x",
        "Rev Growth Est": "15% (Optoelectronics #1 driver)",
        "Monopoly Score": "50% (MOCVD Duopoly w/VECO)",
        "Notes": "Other MOCVD duopoly leader. Optoelectronics is #1 growth driver for 2026. InP laser demand mandatory.",
    },
    "ASMPT": {
        "Alpha Score": "9",
        "Target Upside": "3x",
        "Rev Growth Est": "20% (AMICRA CPO bonders)",
        "Monopoly Score": "Near-monopoly (sub-0.3um bonders)",
        "Notes": "AMICRA division: near-monopoly on sub-0.3um die bonders. Every OSAT/foundry doing CPO must buy AMICRA machines. P/E mid-teens.",
    },
    "6890.T": {
        "Alpha Score": "9",
        "Target Upside": "3x",
        "Rev Growth Est": "15% (TEC demand surge)",
        "Monopoly Score": "80% (Micro-TEC Monopoly)",
        "Notes": "Undisputed king of Micro-TECs. Every optical transceiver needs one to cool the laser. <10x P/E. Textbook buy-and-hold.",
    },
    "LPKF": {
        "Alpha Score": "9",
        "Target Upside": "5x",
        "Rev Growth Est": "50% (LIDE commercialization)",
        "Monopoly Score": "100% (LIDE TGV Patent)",
        "Notes": "Only commercially viable Through-Glass Via (TGV) drilling. Patented LIDE process. Glass substrate supercycle = 5-10x potential.",
    },
    "NDSN": {
        "Alpha Score": "9",
        "Target Upside": "1x-2x",
        "Rev Growth Est": "10% (ASYMTEK underfill)",
        "Monopoly Score": "70% (ASYMTEK Underfill)",
        "Notes": "ASYMTEK division dominates precision dispensing for CPO/CoWoS underfill. Driven by parallel CoWoS expansion.",
    },
    "SMHN.DE": {
        "Rev Growth Est": "30% (HB equipment orders)",
        "Monopoly Score": "45% (Specialized Packaging)",
        "Notes": "Explosive growth in nano-imprint lithography for micro-optics. Pure-play on 2.5D/3D packaging. Overlooked by US retail.",
    },
    "MKSI": {
        "Rev Growth Est": "12% (ESI/Atotech integration)",
        "Monopoly Score": "40% (Laser Via Drilling)",
        "Notes": "ESI/Atotech acquisitions give monopoly on laser drilling micro-vias in GCS and ABF substrates.",
    },
    "CAMT": {
        "Rev Growth Est": "20% (Adv packaging inspection)",
        "Monopoly Score": "50% (2D/3D Metrology)",
        "Notes": "Dominant 2D/3D Optical Metrology for advanced packaging bumps. Direct CPO quality control.",
    },
    "NVMI": {
        "Rev Growth Est": "18% (Metrology expansion)",
        "Monopoly Score": "40% (OCD Metrology)",
        "Notes": "World-class metrology capturing CPO inspection cycles. X-ray and OCD platforms.",
    },
    "IBIEY": {
        "Rev Growth Est": "12% (ABF substrate demand)",
        "Monopoly Score": "35% (High-end Substrates)",
        "Notes": "Dominant high-end IC substrate supplier alongside Shinko. ABF pricing pressure from Palliser activism.",
    },
    "TWCPY": {
        "Rev Growth Est": "15% (CoWoS molding)",
        "Monopoly Score": "70% (Compression Molding)",
        "Notes": "Near-monopoly in precision molding for TSMC CoWoS / Optical packaging lines.",
    },
    "SHWDY": {
        "Rev Growth Est": "10% (Underfill materials)",
        "Monopoly Score": "60% (EMC/Underfill)",
        "Notes": "Massive supplier of critical underfill and EMC for advanced packaging thermal management.",
    },
    "INNO": {
        "Rev Growth Est": "40% (800G/1.6T modules)",
        "Monopoly Score": "30% (China Transceivers)",
        "Notes": "Major Chinese transceiver beneficiary. 800G ramping, 1.6T next. Scale advantage.",
    },
    "EOPT": {
        "Rev Growth Est": "35% (Data center modules)",
        "Monopoly Score": "20% (DC Modules)",
        "Notes": "TFLN modulator pioneer for 1.6T. Data center optical module leader in China.",
    },
    "SMTOY": {
        "Rev Growth Est": "15% (InP supply gap)",
        "Monopoly Score": "60% (InP Substrates)",
        "Notes": "70% InP Supply Gap expected 2025-2026. Japanese quality premium.",
    },
    "DNPCY": {
        "Rev Growth Est": "20% (GCS pilot)",
        "Monopoly Score": "30% (Glass Core R&D)",
        "Notes": "Transforming display IP into Glass Substrates (GCS). Next generation CPO base.",
    },
    "6941.T": {
        "Rev Growth Est": "20% (Test socket demand)",
        "Monopoly Score": "50% (High-speed Optical Sockets)",
        "Notes": "Ultra-high-speed test sockets for 800G/1.6T. Highly profitable. Steep discount to US equivalents.",
    },
    # === CORE PLAYS - fill remaining TBDs ===
    "KLIC": {
        "Rev Growth Est": "40% (Bonder recovery)",
        "Monopoly Score": "35% (TC Bonders)",
        "Notes": "Essential US-listed supplier for thermocompression bonding near optical I/O.",
    },
    "ENTG": {
        "Rev Growth Est": "25% (CMP/Chemicals)",
        "Monopoly Score": "40% (CMP Slurries)",
        "Notes": "Atomic-level polishing chemicals. Mandatory for hybrid bonding surfaces.",
    },
    "ASMIY": {
        "Rev Growth Est": "14% (ALD CAGR 9-13%)",
        "Monopoly Score": "55% (Single-Wafer ALD)",
    },
    "MTSI": {
        "Rev Growth Est": "15% (Optical networking)",
        "Monopoly Score": "30% (Mixed-signal Photonics)",
    },
    "FN": {
        "Rev Growth Est": "12% (Optical assembly)",
        "Monopoly Score": "Critical OEM partner",
    },
    "AMKR": {
        "Rev Growth Est": "10% (Adv packaging ramp)",
        "Monopoly Score": "20% (OSAT)",
    },
    "KLAC": {
        "Rev Growth Est": "8% (Process control)",
        "Monopoly Score": "50% (Wafer Inspection)",
    },
    "VIAV": {
        "Rev Growth Est": "Cyclical recovery",
        "Monopoly Score": "30% (Optical Test)",
    },
    "GLW": {
        "Rev Growth Est": "10% (Fiber/connectivity)",
        "Monopoly Score": "35% (Optical Fiber)",
    },
    "MRVL": {
        "Rev Growth Est": "25% (AI DSP/networking)",
        "Monopoly Score": "Hyper-growth in AI DSP",
    },
    "AVGO": {
        "Rev Growth Est": "15% (Networking silicon)",
        "Monopoly Score": "Dominating CPO Switch",
    },
    "GFS": {
        "Rev Growth Est": "10% (SiPh foundry)",
        "Monopoly Score": "40% (SiPh Foundry)",
    },
    "NVDA": {
        "Rev Growth Est": "50%+ (AI compute)",
        "Monopoly Score": "90% (AI Training GPU)",
    },
    "XSD": {
        "Rev Growth Est": "Market returns",
        "Monopoly Score": "Equal-weight Semi ETF",
    },
    "CLS": {
        "Rev Growth Est": "20% (Networking switches)",
        "Monopoly Score": "Contract Mfg leader",
    },
    "NOVT": {
        "Rev Growth Est": "10% (Precision motion)",
        "Monopoly Score": "Niche (sub-nm alignment)",
    },
    "MTRN": {
        "Rev Growth Est": "8% (Thin-film materials)",
        "Monopoly Score": "70% (Periodic table coverage)",
    },
    "COHU": {
        "Rev Growth Est": "10% (Thermal handlers)",
        "Monopoly Score": "30% (Test Handlers)",
    },
    "APH": {
        "Rev Growth Est": "15% (AI interconnects)",
        "Monopoly Score": "33% (AI DC Interconnect)",
    },
    "MYCRF": {
        "Rev Growth Est": "15% (MRSI bonders)",
        "Monopoly Score": "Competitor to AMICRA",
    },
    "PROB.MI": {
        "Rev Growth Est": "20% (Probe cards)",
        "Monopoly Score": "Rapidly gaining share",
    },
    "ASE": {
        "Rev Growth Est": "20% (6 new plants)",
        "Monopoly Score": "40% (Global OSAT)",
    },
}

# NEW STOCKS TO ADD (from Serenity, Perplexity, Gemini research + user files)
NEW_STOCKS = [
    {
        "Ticker": "5801.T",
        "Company": "Furukawa Electric (FITEL)",
        "Country": "Japan",
        "Bucket": "Hidden",
        "Role": "Remote Laser Sources",
        "Alpha Score": "9",
        "Risk Adj": "7",
        "Hiddenness": "10",
        "Notes": "FITEL brand: highest-power C/O-band CW lasers. NVDA/AVGO/Ayar CPO roadmaps depend on blind-mate ELSFP. Conglomerate discount.",
        "Monopoly Score": "70% (High-Power CW)",
        "Rev Growth Est": "Photonics segment surging",
        "Target Upside": "3x",
    },
    {
        "Ticker": "3105.TW",
        "Company": "Win Semiconductors",
        "Country": "Taiwan",
        "Bucket": "Alpha",
        "Role": "III-V Foundry (InP/GaAs)",
        "Alpha Score": "10",
        "Risk Adj": "7",
        "Hiddenness": "9",
        "Notes": "Foundational to photonics + humanoids + space. AVGO lead customer. Private placement = likely T1 semi (NVDA) taking stake.",
        "Monopoly Score": "60% (III-V Foundry)",
        "Rev Growth Est": "100%+ (Capacity ramp)",
        "Target Upside": "5x",
    },
    {
        "Ticker": "ASX",
        "Company": "ASE Technology (ADR)",
        "Country": "Taiwan",
        "Bucket": "Core",
        "Role": "OSAT / CPO Mass Production",
        "Alpha Score": "9",
        "Risk Adj": "9",
        "Hiddenness": "5",
        "Notes": "CEO confirmed CPO mass production H2 2026. 6 new plants. Largest expansion year ever. The packaging bottleneck.",
        "Monopoly Score": "40% (Global OSAT)",
        "Rev Growth Est": "25% (CPO packaging boom)",
        "Target Upside": "1x-2x",
    },
    {
        "Ticker": "FORM",
        "Company": "FormFactor",
        "Country": "USA",
        "Bucket": "Hidden",
        "Role": "Optical Wafer Probe Cards",
        "Alpha Score": "8",
        "Risk Adj": "7",
        "Hiddenness": "8",
        "Notes": "Specialized optical probe cards for testing SiPh wafers before dicing. 100% mandatory test step.",
        "Monopoly Score": "50% (Optical Probes)",
        "Rev Growth Est": "20% (SiPh test ramp)",
        "Target Upside": "1x-2x",
    },
    {
        "Ticker": "6451.TW",
        "Company": "ShunSin Technology",
        "Country": "Taiwan",
        "Bucket": "Hidden",
        "Role": "SiPh Packaging (Foxconn)",
        "Alpha Score": "8",
        "Risk Adj": "7",
        "Hiddenness": "9",
        "Notes": "Foxconn subsidiary for advanced SiPh packaging. If Foxconn builds NVDA racks, ShunSin handles optical packaging.",
        "Monopoly Score": "Foxconn captive",
        "Rev Growth Est": "50%+ (CPO ramp)",
        "Target Upside": "3x",
    },
    {
        "Ticker": "HPS-A.TO",
        "Company": "Hammond Power Solutions",
        "Country": "Canada",
        "Bucket": "Hidden",
        "Role": "Power transformers for AI DCs",
        "Alpha Score": "7",
        "Risk Adj": "7",
        "Hiddenness": "9",
        "Notes": "Critical power infrastructure for AI data centers. Transformer supply bottleneck.",
        "Monopoly Score": "Niche leader",
        "Rev Growth Est": "30%+ (DC buildout)",
        "Target Upside": "1x-2x",
    },
    {
        "Ticker": "3363.TW",
        "Company": "FOCI Fiber Optic",
        "Country": "Taiwan",
        "Bucket": "Hidden",
        "Role": "Fiber Array Units (FAU)",
        "Alpha Score": "8",
        "Risk Adj": "6",
        "Hiddenness": "9",
        "Notes": "Physical connectors linking fibers to SiPh chips. Tied to Himax WLO. Critical CPO assembly component.",
        "Monopoly Score": "30% (FAU)",
        "Rev Growth Est": "40%+ (CPO assembly)",
        "Target Upside": "3x",
    },
    {
        "Ticker": "4979.TW",
        "Company": "LuxNet Corp",
        "Country": "Taiwan",
        "Bucket": "Hidden",
        "Role": "Active Laser Components",
        "Alpha Score": "8",
        "Risk Adj": "6",
        "Hiddenness": "9",
        "Notes": "Active laser diodes for CPO transceivers. TWSE momentum play in the Taiwan photonics ecosystem.",
        "Monopoly Score": "Taiwan niche",
        "Rev Growth Est": "50%+ (Laser demand)",
        "Target Upside": "3x",
    },
    {
        "Ticker": "CRCL",
        "Company": "Circle Semiconductor",
        "Country": "USA",
        "Bucket": "Moonshot",
        "Role": "Chiplet interconnect IP",
        "Alpha Score": "8",
        "Risk Adj": "4",
        "Hiddenness": "9",
        "Notes": "2x+ YTD per Serenity. Chiplet-to-chiplet interconnect enabling CPO integration.",
        "Monopoly Score": "Emerging IP",
        "Rev Growth Est": "Pre-revenue (IP licensing)",
        "Target Upside": "5x",
    },
    {
        "Ticker": "ENVX",
        "Company": "Enovix",
        "Country": "USA",
        "Bucket": "Hidden",
        "Role": "Advanced battery / energy density",
        "Alpha Score": "7",
        "Risk Adj": "5",
        "Hiddenness": "8",
        "Notes": "Serenity ETF pick. Silicon anode batteries. AI DC power density angle.",
        "Monopoly Score": "Emerging",
        "Rev Growth Est": "Scaling (Fab 2 ramp)",
        "Target Upside": "3x",
    },
]


def main():
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"Loaded {len(rows)} rows from {CSV_PATH}")
    print("=" * 60)
    print("PHASE 1: ENRICHING EXISTING TICKERS FROM RESEARCH...")
    print("=" * 60)

    enriched_count = 0
    for row in rows:
        ticker = row.get("Ticker", "").strip()
        if ticker in ENRICHMENTS:
            e = ENRICHMENTS[ticker]
            changes = []
            for key, val in e.items():
                old = row.get(key, "").strip()
                if (
                    old == "TBD"
                    or old == ""
                    or old == "-"
                    or key in ("Alpha Score", "Target Upside", "Bucket", "Notes")
                ):
                    if key in ("Alpha Score", "Target Upside", "Bucket"):
                        # Only upgrade, don't downgrade
                        if key == "Alpha Score":
                            if int(val) >= int(old or "0"):
                                row[key] = val
                                if val != old:
                                    changes.append(f"{key}: {old}->{val}")
                        elif key == "Target Upside":
                            # Parse multiplier
                            def parse_x(s):
                                s = str(s).strip().lower().replace("x", "")
                                if "-" in s:
                                    return max(float(p) for p in s.split("-"))
                                try:
                                    return float(s)
                                except:
                                    return 1

                            if parse_x(val) >= parse_x(old):
                                row[key] = val
                                if val != old:
                                    changes.append(f"{key}: {old}->{val}")
                        elif key == "Bucket":
                            row[key] = val
                            if val != old:
                                changes.append(f"{key}: {old}->{val}")
                    else:
                        row[key] = val
                        changes.append(f"{key}: TBD->{val[:40]}...")
            if changes:
                enriched_count += 1
                print(f"  [{ticker}] {', '.join(changes[:3])}")

    print(f"\nEnriched: {enriched_count} tickers")
    print("=" * 60)
    print("PHASE 2: ADDING NEW STOCKS FROM RESEARCH...")
    print("=" * 60)

    existing = {r.get("Ticker", "").strip() for r in rows}
    added = 0
    for ns in NEW_STOCKS:
        if ns["Ticker"] not in existing:
            rows.append(ns)
            existing.add(ns["Ticker"])
            added += 1
            print(f"  [NEW] {ns['Ticker']} - {ns['Company']} ({ns['Role']})")

    # Write back
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"\nAdded: {added} new stocks")
    print("=" * 60)
    print("RESEARCH ENRICHMENT COMPLETE.")
    print(f"  Total ecosystem: {len(rows)} plays")
    print(f"  Output: {CSV_PATH}")


if __name__ == "__main__":
    main()
