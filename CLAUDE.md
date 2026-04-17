# Claude Memory Bridge - GIGACPO Terminal

## 🚀 Active Context: V18.2 (News Anti-Spam & Hardening)

### 🧩 Logic & Patterns
1. **Ticker Reconstruction (V10.3)**: 
   - NEVER use greedy regex for cashtags.
   - ALWAYS use `\b` word boundaries for ticker identification.
   - COLLAPSE fragments like `$ N V D A` but do NOT smashed into following words.
   
2. **Translation Turbine (V12.6)**: 
   - Concurrency: 16 workers (ThreadPoolExecutor).
   - Priority: `argostranslate` (Local) > `GoogleTranslator` (API).
   - Rules: No `[EN: Translation]` prefixes. Strip all formatting during flush.
   - Periodic Flush: Update JSON files every 100 posts to maintain live data.

3. **News Intelligence Anti-Spam (V18.2)**
   - `YAHOO_NEWS_MODULE.js` is automatically flattened and rebuilt by `sync_news.py`.
   - Strict `relatedTickers` or `clean_symbol` match required to bypass default Yahoo generic news.

4. **Forensic Recovery (V13.2)**: 
   - Use `engine/forensic_repair.py` if word-smashing reappears.
   - Whitelist of common words (Supply, They, Free) is used to de-ticker false positives.

### 🏛️ File Roles
- `engine/x_intel_deep_scraper.py`: Primary extraction + Live Reconstruction.
- `engine/news_fetcher.py`: Stealth Yahoo News extraction with spam payload filtering.
- `engine/sync_news.py`: Builds flat database/YAHOO_NEWS_MODULE.js asynchronously.
- `engine/translate_intel.py`: High-speed parallel translation.
- `engine/x_intel_instant_sync.py`: Manual sync override.
- `engine/x_intel_daily_sync.py`: Cron-scheduled staggered sync.
- `database/translation_cache.json`: Persistent memory of all translated posts.

### ⚠️ Known Quirks
- Nitter instances often fail under load; the scraper self-evicts bad nodes.
- Windows console requires `UTF-8` override to log CJK characters without crashing.
- `x_intel_master.json` must be rebuilt after every user sync.

[Handover Complete - 2026-04-14]