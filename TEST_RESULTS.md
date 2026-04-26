# Test Execution Results

## Latest Run (Automated Status)
- **Date:** 2026-04-26 00:40:22
- **Status:** ❌ FAILURES DETECTED

### Syntax Audit
- **Result:** PASSED

### Layout Integrity (V28)
- **Result:** PASSED

### Regression Suite
- **Result:** FAIL
- **Error Snippet:**
```
ribute

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
ERROR tests/test_output.txt - UnicodeDecodeError: 'utf-8' codec can't decode ...
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
======================== 6 warnings, 1 error in 34.52s ========================
Total [ERRORS] = 0
sys:1: DeprecationWarning: builtin type swigvarlink has no __module__ attribute

```

### Smoke Test
- **Result:** FAIL
- **Error Snippet:**
```
unsupported operand type(s) for +: 'NoneType' and 'str'
```
