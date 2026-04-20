# GIGACPO Technical Manual & Forensic Review (V22.44)
**Date**: 2026-04-19
**Purpose**: Living manual to guide de-bloating, performance optimization, and project durability.

## 🛡️ Defensive Engineering Principles

1. **Modular Orchestration**: 
   - *Rule*: No script should both "find data" and "generate UI."
   - *Ideal State*: `global_orchestrator.py` conducts; `PipelineOrchestrator` processes.
2. **Idempotency (The "No Duplicate" Law)**:
   - *Rule*: Every sync or repair script must be safe to run 100 times.
   - *Implementation*: Use `SHA-256` titles for news or `tweet_id` for posts.
3. **Signal Governance (The "Noise Filter" Law)**:
   - *Rule*: High-volatility news sources (Jim Cramer, etc.) must be gated at the source.
   - *Implementation*: Maintain a global `NEWS_BLACKLIST` to prevent "Sentiment Garbage-In-Garbage-Out."
4. **Responsive Parity (The "Dual-Surface" Law)**:
   - *Rule*: Emails/UI must define independent Desktop (14-24px) vs Mobile (9-12px) scales.
   - *Implementation*: Use strict `@media` blocks; never rely on single-font auto-scaling.
5. **ASCII-First Data Integrity**:
   - *Rule*: All JSON outputs MUST use `ensure_ascii=True`.
   - *Reason*: Prevents Windows I/O crashes and VS Code "ambiguous unicode" corruption.

## 🚫 The Anti-Pattern Hall of Fame (Do Not Repeat)

- **Ticker Fragmentation ($ N V D A$)**: 
  - *Symptom*: Scrapers or UI logic splitting tickers due to greedy regex.
  - *Fix*: Use `\b` word boundaries and surgical regex in `DataStandardizer`.
- **Function Shadowing (DASHBOARD_DATA DUPLICATION)**:
  - *Symptom*: Copy-pasting JS into `index.html` creates multiple definitions. Last one wins.
  - *Fix*: Strictly use external `.js` modules. No logic in HTML.

## ⛓️ Core Data Pipeline (V20 Flow)

1. **Ingestion**: `x_intel_deep_scraper.py` / `news_fetcher.py`.
2. **Aggregation**: `SocialIntelEngine` / `visual_buzz_aggregator.py`.
3. **Orchestration**: `PipelineOrchestrator` creates UI artifacts.
4. **Deployment**: `RemoteSync` (SFTP).

## 🧹 Optimization Backlog (Actionable Debt)

- [ ] **Consolidate**: Merge `ultimate_repair.py` & `forensic_repair.py` into a unified utility.
- [ ] **Archive**: Move `migrate_vX.py` scripts to `/archive` (Pending regression test).
- [ ] **13F Parity**: Sync Python `IntelligenceEngine` to include the JS +15 conviction boost.
- [ ] **Log Cleanup**: Finalize redirection of all root `.txt` files to `/logs`.

---
## 📜 Decision Log
- **2026-04-18**: Created `CODE-REVIEW.md` to prevent regression of V15.4+ reliability improvements.
- **2026-04-18**: Chose "Hybrid" documentation structure to give future reviewers both high-level principles and specific file-level actionable debt.
