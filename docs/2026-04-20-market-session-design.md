# Design Spec: Multi-Market Session Intelligence & Green Live Badges

## 1. Objective
Stabilize the market session detection to support international exchanges and introduce a "Green Bolt" `L⚡` status for active sessions. Fix layout alignment issues for international tickers in the watchlist.

## 2. Market Detection Logic (Suffix-Aware)
The `get_market_session` function will be upgraded to detect state based on ticker suffixes.

| Suffix | Region | Regular Hours (EST) |
| :--- | :--- | :--- |
| **None / .US** | USA | 09:30 - 16:00 |
| **.DE / .ST / .L / .PA** | Europe | 03:00 - 11:30 |
| **.HK / .N225** | Asia | 21:30 - 04:00 |
| **.AX** | Australia | 19:00 - 01:00 |
| **-USD** | Crypto | 24/7 |

**Session Mapping:**
- **Regular Hours:** `LIVE` (Badge: `L<span style="color:#10b981">⚡</span>`)
- **Before Open:** `PM` (Premarket / 4 hours before)
- **After Close:** `AH` (After Hours / 4 hours after)
- **Other:** `OVN` (Overnight) or `""` (Weekend/Stasis)

## 3. UI Components

### 3.1 The `L⚡` Badge
A specialized high-visibility badge for the regular session.
- **HTML:** `L<span style="color:#10b981">⚡</span>`
- **Background:** `rgba(16,185,129,0.12)`
- **Border:** `1px solid rgba(16,185,129,0.2)`

### 3.2 Watchlist Hardening
- **Width Shift:** Increase ticker column width from **22%** to **26%** to prevent suffix overflow.
- **Sanitization:** Apply `text-overflow: clip` to ensure suffix dots don't trigger layout shifts.

## 4. Implementation Steps
1.  **Refactor `get_market_session`** in `email_market_synopsis.py` to handle suffixes.
2.  **Update `get_session_tag_html`** to support the `LIVE` type with the green bolt.
3.  **Modify `render_bucket`** layout to accommodate wider international labels.
4.  **Harden `get_session_data`** to prioritize `LIVE` flags when technically within open hours.
