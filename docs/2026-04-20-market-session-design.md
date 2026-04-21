# Market Session Design (2026-04-20)

## V23.58 Architecture: US/Eastern Normalization

The market session detection logic has been completely overhauled to eliminate timezone drift across different environments (local VM, GitHub Actions, cloud servers).

### 1. Normalization Protocol
All time calculations within the Sovereign Intelligence Engine now normalize explicitly to US/Eastern (EDT/EST) via `_get_est_now()`. This ensures that session boundaries are identical regardless of the host machine's local timezone.

### 2. High-Fidelity Session Boundaries
The system tracks the exact minute of the trading day and categorizes sessions:
* `PRE`: Morning Session (4 AM - 9:30 AM EST)
* `LIVE`: Regular Market Hours (9:30 AM - 4:00 PM EST). Also handles international overlap based on `.DE`, `.HK`, `.AX` suffixes.
* `AH`: Evening Session (4:00 PM - 8:00 PM EST)
* `OVN`: Overnight / Sunday Futures (8:00 PM - 4:00 AM EST)

### 3. BOATS (Blue Ocean ATS) Discovery
Overnight pricing is now harvested using the hidden `overnightMarketPrice` field by appending `&overnightPrice=true` to the Yahoo Finance API v7 calls. This eliminates the "frozen Friday" problem and provides high-fidelity institutional OVN tracking.

### 4. UI Rendering standard
Badges have strict color coordination to assist visual scanning:
* `PRE` = Orange (`#f59e0b`)
* `LIVE` = Green (`#10b981`)
* `AH` / `POST` = Red (`#ef4444`)
* `OVN` = Amber (`#f59e0b`)
* `PM` = Light Blue (`#60a5fa`)
