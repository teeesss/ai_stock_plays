import csv
import os

def expand_and_enrich_csv(csv_path):
    # New Plays to add
    new_plays = [
        ["GLW", "Corning", "USA", "Core", "Glass Substrates / Fiber", "10", "8", "5", "5-7% (Oligopoly)", "Steady 8-10% CAGR", "Dominates the glass materials needed for next-gen CPO bases."],
        ["SMHN.DE", "SUSS MicroTec", "Germany", "Hidden", "Hybrid Bonding Equipment", "10", "8", "8", "45% (Specialized Packaging)", "Consistent double-digit growth", "Leader in wafer-to-wafer bonding for CPO integration."],
        ["ATS.VI", "AT&S", "Austria", "Hidden", "Advanced IC Substrates", "9", "7", "8", "30% (High-end logic)", "Recovery play 2026", "Scaling glass core substrate R&D for AI/HPC."],
        ["PLET.DE", "Plan Optik", "Germany", "Hidden", "Micro-structured Glass", "9", "6", "9", "80% (Niche Monopoly)", "High growth tied to RF/Photonics", "Crucial for vias and precision glass components in CPO."],
        ["IQE.L", "IQE plc", "UK", "Hidden", "InP Epitaxy", "8", "6", "9", "40% (Global Epi)", "Volatile but high leverage", "Essential foundry for InP optical wafers."],
        ["2455.TW", "Visual Photonics", "Taiwan", "Hidden", "InP / GaAs Foundry", "9", "7", "9", "50% (Taiwan Hub)", "Tied to 800G/1.6T ramps", "The 'TSMC' of the epitaxy world for optical interconnects."],
        ["5201.T", "AGC Inc", "Japan", "Core", "Specialty Glass", "8", "9", "6", "30% (Materials)", "Steady", "Providing base glass chemistry for 3D packaging."],
        ["7741.T", "Hoya Corp", "Japan", "Core", "Glass Substrates/Blanks", "9", "9", "7", "40% (High-end Mask Blanks)", "Consistent", "Crucial for the extreme precision required in SiPh lithography."],
        ["LITE", "Lumentum", "USA", "Core", "UHP CW Lasers", "10", "7", "4", "50% (CW Laser Market)", "FY27: $500M CPO Revenue target", "Major purchase orders secured for high-power lasers used in CPO."],
        ["AMAT", "Applied Materials", "USA", "Core", "Packaging Equipment", "10", "9", "3", "30% (Overall WFE)", "Driven by AI packaging", "Providing the tools for glass substrate and SiPh fabrication."],
        ["TYO:6028", "TechnoPro", "Japan", "Hidden", "Specialized Engineering", "7", "8", "9", "20%", "Steady", "Supplying the scarce engineering talent for SiPh integration lines."],
        ["FRA:MRK", "Merck KGaA", "Germany", "Core", "Specialized Chemicals", "9", "9", "5", "Oligopoly in CMP chemicals", "Steady", "Crucial for Atomic Layer Deposition and CMP polishing in SiPh."],
        ["SCHN.PA", "Schneider Electric", "France", "Core", "Data Center Infrastructure", "8", "9", "4", "Oligopoly", "Steady", "Energy bottleneck play; CPO reduces power consumption, boosting SCHN efficiency."],
        ["VRT", "Vertiv", "USA", "Core", "Liquid Cooling", "9", "8", "5", "High (AI Data Centers)", "Hyper-growth", "CPO reduces thermal load but density still requires Vertiv."],
        ["SMTC", "Semtech", "USA", "Core", "Linear Drive / TIA", "9", "7", "6", "30%", "Driven by LPO/CPO", "Crucial analog front-end components for optical engines."],
        ["PSTG", "Pure Storage", "USA", "Core", "All-Flash Data", "8", "8", "5", "Storage Alpha", "Steady", "AI clusters need fast storage tied to the broad photonics fabric."],
        ["ALAB", "Astera Labs", "USA", "Core", "PCIe / CXL Retimers", "10", "7", "4", "Oligopoly", "Hyper-growth", "The copper-side equivalent of the CPO bottleneck."],
    ]

    # Load existing rows
    rows = []
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Dedup and Merge
    existing_tickers = {r[0].strip() for r in rows}
    
    for play in new_plays:
        if play[0] not in existing_tickers:
            rows.append(play)

    # Sort by Alpha Score descending
    rows.sort(key=lambda x: int(x[5]) if x[5].isdigit() else 0, reverse=True)

    # Write back
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    
    print(f"Dataset expanded. Total plays: {len(rows)}")

if __name__ == "__main__":
    expand_and_enrich_csv('cpo_master_ultimate.csv')