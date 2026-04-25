# Test Execution Results

## Latest Run (Automated Status)
- **Date:** 2026-04-24 22:18:34
- **Status:** ❌ FAILURES DETECTED

### Syntax Audit
- **Result:** PASSED

### Layout Integrity (V26.7)
- **Result:** PASSED

### Regression Suite
- **Result:** FAIL
- **Error Snippet:**
```
precationWarning: builtin type SwigPyObject has no __module__ attribute

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
ERROR tests/test_email_synopsis.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
======================== 6 warnings, 1 error in 40.58s ========================
sys:1: DeprecationWarning: builtin type swigvarlink has no __module__ attribute

```

### Smoke Test
- **Result:** PASSED

