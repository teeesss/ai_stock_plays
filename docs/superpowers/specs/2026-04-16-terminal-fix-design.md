# Design Document: Terminal Fixes (2026-04-16)

## Problem Statement
1. **Intelligence Terminal Date Lag**: Social posts from 4/16 are showing as 4/15 in the UI because the UTC 00:00 timestamp shifts backward when converted to local browser time in Western timezones.
2. **Broken Sorting**: The "Day $" column incorrectly sorts by percentage, and the "% Chg" column sorting is not implemented in the JS `sortFn`.
3. **Missing Feedback**: Users cannot verify when the social intelligence data was last updated.

## Proposed Changes

### 1. UI Infrastructure (cpo_plays.html)
- **Timestamp Addition**:
    - Modify the `intel-header` div to include a new span for the global intelligence timestamp.
    - Path: `window.X_INTEL_MODULE.visual_last_updated` (ISO string).
    - Display format: `YYYY-MM-DD HH:MM EST`.
- **Date Display Fix**:
    - In `renderIntel`, stop using `toLocaleDateString()`.
    - Extract the date component directly from the `p.timestamp` string (e.g., `p.timestamp.split('T')[0]`).

### 2. Logic Layer (cpo_plays.html - script)
- **Sorting Core**:
    - Update `sortFn` cases:
        - `today` -> use `a.todayChg` (Realized dollar move).
        - `todayPct` -> use `a.todayPct` (Percentage move).
- **Consolidation**:
    - Remove duplicate `setSort` definition (lines 632 vs 712). Keep the `window.setSort` version which defaults to descending (`-1`).

### 3. Data Integrity
- Ensure `live_prices.js` contains the latest `_meta` fields. (Already verified in logs, just confirming UI consumption).

## Success Criteria
- Posts on 4/16/2026 display "2026-04-16" in the social terminal.
- Clicking "Day $" sorts by largest absolute dollar change (descending).
- Clicking "% Chg" sorts by largest percentage change (descending).
- Social modal shows "LATEST INTELLIGENCE: [TIME]" in the header.
