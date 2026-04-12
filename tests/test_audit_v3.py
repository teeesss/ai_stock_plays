import asyncio
import sys
import os

# Ensure the script can find dependencies
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'research'))

from financial_auditor import audit_financials

async def run_test():
    print("🔬 INITIALIZING V3.0 AUDIT TEST (GLOBAL VARIETY)...")
    
    # Create a temporary test CSV
    test_csv = 'research/test_audit_list.csv'
    with open(test_csv, 'w', encoding='utf-8') as f:
        f.write("Ticker,Company,Country,Status,Bucket,Role,Alpha Score,Risk Adj,Hiddenness,Notes,Monopoly Score,Rev Growth Est,Target Upside\n")
        f.write("NVDA,NVIDIA,USA,Public,Core,GPU,6,10,2,Test,Infinite,50%,1x\n")
        f.write("ASMPT,ASMPT,Hong Kong,Public,Hidden,Die bonders,9,8,9,Test,90%,20%,3x\n")
        f.write("3105.TW,Win Semi,Taiwan,Public,Alpha,Foundry,10,7,9,Test,60%,100%,5x\n")
        f.write("AIXNY,Aixtron,Germany,Public,Hidden,MOCVD,9,8,8,Test,50%,15%,1x\n")
        f.write("5713.T,Sumitomo Metal,Japan,Public,Hidden,Indium,9,8,10,Test,90%,12%,2x\n")

    await audit_financials(test_csv)
    
    print("\n✅ TEST COMPLETE. Check 'research/' for the latest snapshot JSON and audit_failures.log.")

if __name__ == "__main__":
    asyncio.run(run_test())
