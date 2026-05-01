# Test Execution Results

## Latest Run (Automated Status)
- **Date:** 2026-05-01 14:48:27
- **Status:** FAILURES DETECTED

### Syntax Audit
- **Result:** PASSED

### Layout Integrity (V28)
- **Result:** PASSED

### Regression Suite
- **Result:** FAIL
- **Error Snippet:**
```
 (most recent call last):
  File "X:\COS_Stock_Plays\tests\test_sovereign_engine.py", line 25, in test_pulse_bar_renaming
    self.assertIn("S&P", html)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "C:\Python314\Lib\unittest\case.py", line 1189, in assertIn
    if member not in container:
       ^^^^^^^^^^^^^^^^^^^^^^^
TypeError: argument of type 'coroutine' is not a container or iterable

----------------------------------------------------------------------
Ran 130 tests in 2.485s

FAILED (errors=1)

```
