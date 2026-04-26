import csv
import os


def moonshot_enrichment(csv_path):
    # Data-driven Moonshots and Rev Targets
    # Targets based on scaling from pilot (~$5M-$10M) to volume production (~$100M-$500M)
    enrichment_map = {
        "POET": {
            "Rev": "1500% Potential (Pilot to $100M+)",
            "Monopoly": "90% (Optical Interposer)",
            "Bucket": "Moonshot",
            "Alpha": "10",
        },
        "LWLG": {
            "Rev": "500%+ Potential (Phase II Vol)",
            "Monopoly": "80% (Polymer Modulator)",
            "Bucket": "Moonshot",
            "Alpha": "10",
        },
        "AAOI": {
            "Rev": "300% (1.6T Hyperscale pivot)",
            "Monopoly": "25% (Transceiver)",
            "Bucket": "Moonshot",
            "Alpha": "9",
        },
        "AXTI": {
            "Rev": "200-300% (InP Substrate Gap)",
            "Monopoly": "40% (Oligopoly)",
            "Bucket": "Moonshot",
            "Alpha": "9",
        },
        "ALAB": {
            "Rev": "250% (Aries/Leo PCIe Ramp)",
            "Monopoly": "50% (Retimer leader)",
            "Bucket": "Moonshot",
            "Alpha": "10",
        },
        "LITE": {
            "Rev": "400% (CPO Laser segment ramp)",
            "Monopoly": "50% (UHP CW Diodes)",
            "Bucket": "Core",
            "Alpha": "10",
        },
        "CRDO": {
            "Rev": "FY26: 200%+ realization",
            "Monopoly": "35% (DSP)",
            "Bucket": "Core",
            "Alpha": "10",
        },
        "BESIY": {
            "Rev": "250% (HB Tool demand)",
            "Monopoly": "75% (Hybrid Bonding)",
            "Bucket": "Core",
            "Alpha": "10",
        },
        "PLET.DE": {
            "Rev": "300% (TGV Glass packaging)",
            "Monopoly": "85% (Niche)",
            "Bucket": "Moonshot",
            "Alpha": "9",
        },
        "2455.TW": {
            "Rev": "300% (Foundry capacity tight)",
            "Monopoly": "50% (Epi Foundry)",
            "Bucket": "Moonshot",
            "Alpha": "10",
        },
    }

    more_plays = [
        [
            " CelestialAI",
            "Marvell/CelestialAI",
            "USA",
            "Hidden",
            "Optical Compute Fabric",
            "10",
            "60%",
            "4",
            "300% (Segment internal)",
            "Acquired tech integration into Teralynx/Marvell.",
        ],
        [
            "AYAR",
            "Ayar Labs",
            "USA",
            "Hidden",
            "TeraPHY Optical I/O",
            "10",
            "80%",
            "9",
            "500% (Pre-revenue ramp)",
            "Private but tracking via Intel/Nvidia partnerships.",
        ],
        [
            "SCINTIL",
            "Scintil Photonics",
            "France",
            "Hidden",
            "III-V on Si Integration",
            "9",
            "50%",
            "9",
            "400% (Scaling SoC)",
            "Foundry partner for monolithic integration.",
        ],
        [
            "RANV",
            "Ranovus",
            "Canada",
            "Hidden",
            "Odin Photonic Engine",
            "10",
            "60%",
            "9",
            "300% (Hyperscale ramp)",
            "Direct interface with 51.2T switches.",
        ],
    ]

    # Load existing
    rows = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Apply enrichment
    for row in rows:
        ticker = row[0].strip()
        if ticker in enrichment_map:
            e = enrichment_map[ticker]
            row[9] = e["Rev"]
            row[8] = e["Monopoly"]
            row[3] = e["Bucket"]
            row[5] = e["Alpha"]

    # Add hidden moonshots if missing
    existing = {r[0].strip() for r in rows}
    for play in more_plays:
        if play[0].strip() not in existing:
            rows.append(play)

    # Sort
    rows.sort(key=lambda x: int(x[5]) if len(x) > 5 and x[5].isdigit() else 0, reverse=True)

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # Sync
    os.system("python research/sync_data.py")
    print(f"MOONSHOT ENRICHMENT COMPLETE. Total plays: {len(rows)}")


if __name__ == "__main__":
    moonshot_enrichment("cpo_master_ultimate.csv")
