import csv

rows = list(csv.reader(open('cpo_master_ultimate.csv', encoding='utf-8')))
updates = {
    'CRDO': ('30% (Oligopoly vs MRVL/ALAB)', 'FY26: >200% / FY27: >50%'),
    'BESIY': ('75% (Dominates Hybrid Bonding)', 'Multi-year inflection (Market CAGR 22%)'),
    'ONTO': ('40% (Duopoly vs KLAC)', 'FY26: >25% (HBM/Packaging >30%)'),
    'COHR': ('50% (CW Laser Duopoly)', 'FY26: 19.4% / FY27: 23.2%'),
    'ALRIB.PA': ('100% (Industrial MBE)', 'Tied to new datacom contracts'),
    'NDSN': ('70% (ASYMTEK Underfill)', 'Driven by parallel CoWoS expansion'),
    'SMTOY': ('60% (InP Substrates)', '70% Supply Gap expected 2025-2026'),
    'AXTI': ('35% (InP Substrates)', 'High volatility due to export controls'),
    'ASMIY': ('55% (Single-Wafer ALD)', 'FY26: 14% (ALD CAGR 9-13%)'),
    'LWLG': ('100% (If Perkinamine wins)', 'Pre-revenue (10x potential)'),
    'GFS': ('40% (SiPh Foundry)', 'SiPh segment hitting $1B by 2028'),
    'TSEM': ('40% (SiPh Foundry)', 'High growth tied to custom PDKs')
}

header = rows[0]
new_rows = [header]

for r in rows[1:]:
    ticker = r[0].strip()
    if ticker in updates:
        r[8] = updates[ticker][1] # Rev Growth Est
        r[9] = updates[ticker][0] # Monopoly Score
    new_rows.append(r)

with open('cpo_master_ultimate.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)