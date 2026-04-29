# Test Execution Results

## Latest Run (Automated Status)
- **Date:** 2026-04-29 12:07:47
- **Status:** FAILURES DETECTED

### Syntax Audit
- **Result:** PASSED

### Layout Integrity (V28)
- **Result:** PASSED

### Regression Suite
- **Result:** FAIL
- **Error Snippet:**
```
ary()\n\n        # 2. Print Intelligence Line\n        print(f"[EMAIL] Intelligence: {subject}")\n\n        # 3. Print Final Dispatch Confirmation\n        dispatch_ts = (\n            datetime.datetime.now().strftime("%a %b %d %I:%M:%S %p %Z %Y").replace("  ", " ")\n        )\n        print(f"Dispatched at {dispatch_ts}: SIE Pulse")\n' : price_str should use reg_price

----------------------------------------------------------------------
Ran 134 tests in 2.100s

FAILED (failures=7, errors=11)

```

### Smoke Test
- **Result:** FAIL
- **Error Snippet:**
```
_Stock_Plays\\engine\\visual_buzz_aggregator.py']' returned non-zero exit status 1.

============================================================
   SUMMARY: 3/7 Steps Succeeded
============================================================
   ⚠️ PIPELINE HAS DEGRADED — AUDIT LOGS IMMEDIATELY
Traceback (most recent call last):
  File "X:\COS_Stock_Plays\engine\inst_13f_fetcher.py", line 27, in <module>
    from yahooquery import Ticker as YQTicker
ModuleNotFoundError: No module named 'yahooquery'

```
