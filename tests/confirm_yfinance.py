import asyncio
import sys
from financial_auditor import audit_financials

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    print("Verification: Proving yfinance Extraction via Stealth Navigator...")
    # Run a small batch (first 3 tickers)
    await audit_financials('cpo_master_ultimate.csv', max_tickers=3)
    
    # Now explicitly read the CSV to show the user the updated values
    import csv
    with open('cpo_master_ultimate.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        notes_idx = header.index('Notes')
        for i, row in enumerate(reader):
            if i < 3:
                ticker = row[0]
                notes = row[notes_idx]
                if "Valuation:" in notes:
                    print(f"  [SUCCESS] {ticker} -> Found Data: {notes.split('Valuation:')[-1]}")
                else:
                    print(f"  [ERROR] {ticker} -> No valuation data found in Notes.")

if __name__ == "__main__":
    asyncio.run(main())
