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

### 4. Time-Anchored Windowing (V23.86 Hardening)
To combat stale `marketState` flags from Yahoo, the engine now uses clock-based windows to force-prioritize data fields:
* **4:00 - 9:30 AM EST**: Forced prioritization of `preMarketPrice`.
* **16:00 - 20:00 PM EST**: Forced prioritization of `postMarketPrice`.
* **20:00 - 4:00 AM EST**: Forced prioritization of `overnightMarketPrice`.

### 5. Atomic Session Overrides
Data integrity is maintained by treating Price and Percentage as an atomic unit. If a session change is detected, both fields must be updated simultaneously to prevent "mixed state" rendering ($REG + %EXT).

### 6. Midpoint Fallback
For low-volume assets where `preMarketPrice` returns null, the engine calculates the average of `bid` and `ask` to maintain real-time volatility tracking.

### 4. UI Rendering standard
Badges have strict color coordination to assist visual scanning:
* `PRE` = Orange (`#f59e0b`)
* `LIVE` = Green (`#10b981`)
* `AH` / `POST` = Red (`#ef4444`)
* `OVN` = Amber (`#f59e0b`)
* `PM` = Light Blue (`#60a5fa`)
