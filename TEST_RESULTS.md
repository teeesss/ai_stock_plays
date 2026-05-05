# Test Execution Results

## Latest Run (Automated Status)
- **Date:** 2026-05-05 07:47:16
- **Status:** FAILURES DETECTED

### Syntax Audit
- **Result:** PASSED

### Layout Integrity (V28)
- **Result:** PASSED

### Regression Suite
- **Result:** FAIL
- **Error Snippet:**
```
e.py", line 35, in test_sentiment_accuracy
    self.assertNotEqual(
    ~~~~~~~~~~~~~~~~~~~^
        sentiment["market"]["value"],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        62,
        ^^^
        "Market F&G is stuck on fake placeholder 62",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: 62 == 62 : Market F&G is stuck on fake placeholder 62

----------------------------------------------------------------------
Ran 130 tests in 4.199s

FAILED (failures=1)

```
