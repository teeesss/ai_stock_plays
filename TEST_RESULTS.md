# Test Execution Results

## Latest Run (Automated Status)
- **Date:** 2026-04-29 12:30:14
- **Status:** FAILURES DETECTED

### Syntax Audit
- **Result:** PASSED

### Layout Integrity (V28)
- **Result:** PASSED

### Regression Suite
- **Result:** FAIL
- **Error Snippet:**
```
mary()\n\n        # 2. Print Intelligence Line\n        print(f"[EMAIL] Intelligence: {subject}")\n\n        # 3. Print Final Dispatch Confirmation\n        dispatch_ts = (\n            datetime.datetime.now().strftime("%a %b %d %I:%M:%S %p %Z %Y").replace("  ", " ")\n        )\n        print(f"Dispatched at {dispatch_ts}: SIE Pulse")\n' : ext_html should use ext_price

----------------------------------------------------------------------
Ran 134 tests in 1.787s

FAILED (failures=7, errors=11)

```
