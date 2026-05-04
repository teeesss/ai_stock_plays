import asyncio
import json
import logging
import random
import sys
import time

import feedparser

# V28: Setup Logging BEFORE any local imports that might hijack root
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ── LOCAL IMPORTS (Must be after logging setup) ──────────────────────
import re
import urllib.parse
from pathlib import Path

import yaml
from curl_cffi.requests import AsyncSession

try:
    from error_monitor import init_error_monitor
    from paywall_intelligence import PaywallIntelligence
except ImportError:
    from engine.error_monitor import init_error_monitor
    from engine.paywall_intelligence import PaywallIntelligence

init_error_monitor()

ROOT = Path(__file__).parent.parent
LIVE_PRICES_JSON = ROOT / "database" / "live_prices.json"
MACRO_NEWS_CACHE = ROOT / "database" / "macro_news_cache.json"
VELOCITY_PULSE_DB = ROOT / "database" / "macro_velocity_metrics.json"
MACRO_CONFIG_PATH = ROOT / "config" / "macro_config.yaml"


class MacroAggregator:
    def __init__(self):
        self.velocity_pulse = {}

        # V27: Config-First Architecture — load from YAML, fallback to defaults
        cfg = self._load_config()

        self.priority_keywords = cfg.get(
            "priority_keywords",
            [
                "SEMICONDUCTOR",
                "SEMI",
                "CHIP",
                "NVIDIA",
                "BLACKWELL",
                "PHOTONICS",
                "CPO",
                "HBM",
                "EARNINGS",
                "REVENUE",
                "IPO",
            ],
        )
        self.institutional_keywords = cfg.get(
            "institutional_keywords",
            [
                "GOLDMAN SACHS",
                "JPMORGAN",
                "MORGAN STANLEY",
                "BLACKROCK",
            ],
        )
        self.priority_keywords.extend(self.institutional_keywords)

        # V27: Bonus Keywords — variable-point high-signal terms
        self.bonus_keywords = cfg.get("bonus_keywords", {})

        # V27: Cluster Bonus — multiplicative boost for multi-signal headlines
        self.cluster_terms = cfg.get(
            "cluster_terms",
            [
                "CPO",
                "PHOTONICS",
                "1.6T",
                "NVIDIA",
                "HBM",
                "BLACKWELL",
            ],
        )
        # V28: Unified Scoring Rules
        self.scoring_rules = cfg.get("scoring_rules", {})
        self.priority_keyword_weight = self.scoring_rules.get("priority_keyword_weight", 50)
        self.anchor_word_weight = self.scoring_rules.get("anchor_word_weight", 200)
        self.blacklist_penalty = self.scoring_rules.get("blacklist_penalty", -1000)
        self.relevance_floor_penalty = self.scoring_rules.get("relevance_floor_penalty", 0)
        self.billion_scale_bonus = self.scoring_rules.get("billion_scale_bonus", 45)
        self.cluster_multiplier = self.scoring_rules.get("cluster_multiplier", 1.55)

        # Safe Regex Compilation
        regex_pattern = self.scoring_rules.get(
            "billion_scale_regex", r"\$?\s?\d+(\.\d+)?\s?(B|BN|BILLION|TRILLION)"
        )
        try:
            self.billion_regex = re.compile(regex_pattern, re.IGNORECASE)
        except re.error:
            log.warning(
                "[CONFIG ERROR] Invalid billion_scale_regex in YAML. Falling back to default."
            )
            self.billion_regex = re.compile(
                r"\$?\s?\d+(\.\d+)?\s?(B|BN|BILLION|TRILLION)", re.IGNORECASE
            )

        self.untrusted_aggregators = cfg.get("untrusted_aggregators", ["Google News"])

        # V27: Anchor Words — massive macro anchors (+200)
        self.anchor_words = cfg.get(
            "anchor_words",
            [
                "MARKET OVERVIEW",
                "WALL ST",
                "CLOSING BELL",
                "OPENING BELL",
                "RECAP",
                "STOCKS FALL",
                "STOCKS RISE",
                "STOCK MARKET TODAY",
            ],
        )

        self.priority_tickers = cfg.get(
            "priority_tickers",
            [
                "NVDA",
                "AMD",
                "AVGO",
                "ALAB",
                "ARM",
                "MRVL",
                "LITE",
                "FN",
                "COHR",
                "LUNA",
                "PII",
                "RMBS",
                "INTC",
                "TSM",
                "HIVE",
            ],
        )

        self.feeds = cfg.get(
            "feeds",
            {
                "WSJ Markets": {
                    "url": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
                    "type": "rss",
                    "weight": 150,
                },
                "CNBC Earnings": {
                    "url": "https://www.cnbc.com/id/15839135/device/rss/rss.html",
                    "type": "rss",
                    "weight": 170,
                },
            },
        )

        self.MAX_PER_SOURCE = cfg.get("max_per_source", 5)

        self.SCRAPE_JUNK_TITLES = frozenset(
            [
                "entertainment",
                "news",
                "life",
                "sports",
                "opinion",
                "politics",
                "technology",
                "science",
                "health",
                "travel",
                "food",
                "style",
                "videos",
                "photos",
                "podcasts",
                "newsletters",
                "subscribe",
                "sign in",
                "log in",
                "markets",
                "finance",
                "more",
            ]
        )

        self.blacklist = cfg.get(
            "blacklist",
            [
                "DAVE RAMSEY",
                "PR NEWSWIRE",
                "BUSINESS WIRE",
                "GLOBE NEWSWIRE",
                "NANCY PELOSI",
                "JIM CRAMER",
                "WARREN BUFFETT",
                "WARREN BUFFET",
                "TERRY SAVAGE",
            ],
        )

        self.forbidden_domains = set(
            cfg.get(
                "forbidden_domains",
                [
                    "aol.com",
                    "msn.com",
                    "fool.com",
                    "motleyfool.com",
                ],
            )
        )

        # V28: source_space_map loaded from YAML — Normalized to uppercase for case-insensitive lookup
        raw_map = cfg.get("source_space_map", {})
        self.SOURCE_SPACE_MAP = {str(k).upper().replace(" ", ""): v for k, v in raw_map.items()}

        # V28: google_news_whitelist loaded from YAML
        self.google_news_whitelist = {
            str(s).upper().replace(" ", "") for s in cfg.get("google_news_whitelist", [])
        }

        # V28: Auto-badge formatting rules (fallback when source not in SOURCE_SPACE_MAP)
        badge_rules = cfg.get("auto_badge_rules", {})
        self.BADGE_ACRONYM_MAX = badge_rules.get("acronym_max_length", 5)
        self.BADGE_CAMEL_SPLIT = badge_rules.get("camel_split", True)

        # V28: Pre-extract domain fragments for fast source-name blocking
        self.forbidden_source_frags = {d.split(".")[0].lower() for d in self.forbidden_domains}

        # V28: Initialize Hierarchy Leader for temporal logic
        try:
            from market_session import MarketSession

            self.market_session = MarketSession()
        except ImportError:
            from engine.market_session import MarketSession

            self.market_session = MarketSession()

        log.info(
            f"[V28] Config loaded: {len(self.priority_keywords)} keywords, {len(self.bonus_keywords)} bonus terms, {len(self.feeds)} feeds, {len(self.priority_tickers)} tickers, {len(self.SOURCE_SPACE_MAP)} source overrides"
        )

    def _load_config(self):
        """V27: Loads config/macro_config.yaml with robust fallback to empty dict."""
        if not MACRO_CONFIG_PATH.exists():
            log.warning(f"[CONFIG] {MACRO_CONFIG_PATH} not found. Using hardcoded defaults.")
            return {}
        try:
            with open(MACRO_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            if not isinstance(cfg, dict):
                log.warning("[CONFIG] YAML parsed but is not a dict. Using defaults.")
                return {}
            log.info(
                f"[CONFIG] Loaded macro_config.yaml ({MACRO_CONFIG_PATH.stat().st_size} bytes)"
            )
            return cfg
        except Exception as e:
            log.error(f"[CONFIG] YAML parse error: {e}. Using hardcoded defaults.")
            return {}

    def normalize_source(self, name):
        """V26.13: Normalizes source badges with proper spacing and branding."""
        s_upper = name.upper().replace(".COM", "").replace(" ", "")
        return self.SOURCE_SPACE_MAP.get(s_upper, name.upper())

    def _load_prices(self):
        if not LIVE_PRICES_JSON.exists():
            return {}
        try:
            with open(LIVE_PRICES_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def is_article_safe(self, title, link, source, summary="", feed_name=""):
        """V26.10: Central gate for domain, personality, and language filtering."""
        t_upper = title.upper()
        l_lower = link.lower()
        s_upper = source.upper()
        sum_upper = summary.upper()
        fn_upper = feed_name.upper()

        # 0. V28: Aggregator Whitelist Gate
        # If this article comes from an untrusted aggregator, it MUST be in the Top 20 whitelist.
        if any(agg.upper() in fn_upper for agg in self.untrusted_aggregators):
            # Check source name (e.g., "Reuters")
            norm_source = s_upper.replace(" ", "")
            is_whitelisted = norm_source in self.google_news_whitelist

            # Fallback: Check domain fragment if source name is ambiguous
            if not is_whitelisted:
                link_domain = urllib.parse.urlparse(link).netloc.lower()
                for wl_item in self.google_news_whitelist:
                    # Very loose match for domains (e.g., 'reuters' in 'reuters.com')
                    if wl_item.lower() in link_domain:
                        is_whitelisted = True
                        break

            if not is_whitelisted:
                log.debug(f"  [BLOCKED] Non-whitelist source from aggregator: '{source}' ({link})")
                return False

        # 1. Domain Hard Blacklist — direct URL check
        if any(d in l_lower for d in self.forbidden_domains):
            return False

        # 1b. V28: Source-Name Domain Fragment Check (catches Google News proxied URLs)
        # Google News wraps links as news.google.com/rss/... hiding the real publisher domain.
        # Only run this fuzzy check if the item came from an untrusted aggregator.
        if any(agg.upper() in fn_upper for agg in self.untrusted_aggregators):
            src_lower = source.lower()
            if any(frag in src_lower for frag in self.forbidden_source_frags):
                log.debug(f"  [BLOCKED] Forbidden source via display_source: '{source}'")
                return False

        # 2. Personality/Source Metadata Blacklist
        forbidden_terms = self.blacklist + ["MOTLEY FOOL", "AOL", "MSN"]
        for term in forbidden_terms:
            if term in t_upper or term in s_upper or term in sum_upper:
                return False

        # 3. Language Gate (English Only Heuristic)
        if not self.is_english(title):
            return False

        # 4. Length Gate (V26.13 Architect Mandate)
        # Purge nav items or low-context fragments (e.g., "Macroscope")
        words = title.split()
        if len(words) < 4:
            return False

        # 5. Opinion / Clickbait Gate (V26.13)
        # Purge interrogative/instructional filler (Why/How/Should/Can)
        # Institutional news is declarative.
        if title.endswith("?"):
            return False

        opinion_markers = ["WHY ", "HOW TO ", "SHOULD I ", "CAN YOU ", "WHAT TO KNOW"]
        if any(t_upper.startswith(m) for m in opinion_markers):
            return False

        # 6. Video Purge (V26.11 Architect Mandate)
        # Avoid blocking articles *about* video tech by checking for path/param markers
        if any(v in l_lower for v in ["/video/", "video.html", "?video="]):
            return False

        # 7. Geographic/Niche Noise Filter (V26.11)
        # Purge niche local news unless it carries global tech alpha (TSMC, ASML, etc.)
        niche_markers = ["INDIA", "RBL BANK", "NIGERIA", "PAKISTAN", "LOCAL BANK"]
        tech_anchors = [
            "NVIDIA",
            "CHIP",
            "SEMI",
            "ASML",
            "AI",
            "TSMC",
            "INTEL",
            "AMD",
            "BLACKWELL",
        ]
        if any(m in t_upper for m in niche_markers):
            if not any(a in t_upper for a in tech_anchors):
                return False

        return True

    def is_fresh_enough(self, ts, is_semi=False):
        """V28 Hardened: articles older than 36h (Weekday) or 60h (Weekend).
        Top Hierarchy: SEMI articles can go back 2 weeks (336h)."""
        age_hours = (time.time() - ts) / 3600

        if is_semi:
            return age_hours <= 336  # 14 days

        limit = 60 if self.market_session.is_market_stasis() else 36

        # V29.7: Sunday/Monday Lenience (72h limit)
        now_est = self.market_session.get_est_now()
        day = now_est.weekday()  # Mon=0, Sun=6
        if day == 6 or day == 0:
            limit = 72

        return age_hours <= limit

    def apply_freshness_decay(self, score, ts, is_semi=False):
        """V28 Hardened: 50% penalty for articles older than 24h (Weekday) or 48h (Weekend).
        Top Hierarchy: SEMI articles exempt from decay for 14 days."""
        age_hours = (time.time() - ts) / 3600

        if is_semi:
            return score  # No decay for semi trade news within 14d

        decay_limit = 48 if self.market_session.is_market_stasis() else 24
        if age_hours > decay_limit:
            return score * 0.5
        return score

    def is_english(self, text):
        """Lightweight heuristic to detect non-English/Foreign scripts."""
        if not text:
            return True

        # 1. Check for common English "anchor" words
        common_english = {
            " THE ",
            " AND ",
            " FOR ",
            " WITH ",
            " IN ",
            " ON ",
            " TO ",
            " IS ",
            " OF ",
            " AT ",
            " AMID ",
            " BY ",
            " FROM ",
            " AS ",
        }
        t_pad = f" {text.upper()} "
        has_anchors = any(w in t_pad for w in common_english)

        # 2. Check for technical tickers or keywords that imply English finance news
        finance_anchors = {
            "STOCK",
            "MARKET",
            "NVIDIA",
            "TECH",
            "PRICE",
            "SURGE",
            "FALL",
            "GAIN",
            "CHIP",
            "SEMI",
            "INFLATION",
            "EARNINGS",
            "FED ",
            "RATE",
            "ECONOMY",
            "GUIDANCE",
            "FORECAST",
            "REVENUE",
            "CPO",
            "GPU",
            "AI ",
            "TSMC",
            "ASML",
            "INTC",
            "AMD",
            "META",
            "GOOG",
            "AMZN",
            "MSFT",
        }
        has_finance = any(w in t_pad for w in finance_anchors)

        # 3. Unicode script check
        try:
            text.encode("ascii")
            # If it's ASCII but has zero English or Finance anchors, it's likely a foreign Latin language (French, etc.)
            if not has_anchors and not has_finance and len(text.split()) > 2:
                return False
            return True
        except UnicodeEncodeError:
            # Contains non-ASCII (CJK, Cyrillic, etc.)
            non_ascii = [c for c in text if ord(c) > 127]
            # If more than 10% is non-ASCII, it's definitely foreign
            if len(non_ascii) / len(text) > 0.1:
                return False
            # If it has some accents but also English anchors, we allow it (e.g. "Nvidia's rôle")
            return has_anchors or has_finance

    async def resolve_redirect(self, url, session=None):
        """V26.10: Lightweight HEAD request to resolve tracking links (Approach C-Lite)."""
        # Targeted resolution only for known aggregators to minimize latency
        if not any(d in url.lower() for d in ["google.com/url", "aol.com"]):
            return url
        try:
            # V29.7.1: Reuse existing session to avoid handshake overhead
            if session:
                res = await session.head(url, timeout=1.5, allow_redirects=True)
                return str(res.url)

            async with AsyncSession(impersonate="chrome124") as s:
                res = await s.head(url, timeout=1.5, allow_redirects=True)
                return str(res.url)
        except Exception as e:
            log.debug(f"  [!] Redirect resolution failed for {url}: {e}")
            return url

    def score_headline(self, title, source_name):
        """V28: Decoupled Scoring - returns (content_score, base_weight)."""
        t_upper = title.upper()

        # Blacklist enforcement
        for bl in self.blacklist:
            if bl in t_upper:
                return (self.blacklist_penalty, 0)

        # Base weight from source feed
        base_weight = self.feeds.get(source_name, {}).get("weight", 10)
        content_score = 0

        # Standard keyword bonus
        for kw in self.priority_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", t_upper):
                content_score += self.priority_keyword_weight

        # V27: Bonus Keywords - variable points from config
        for kw, points in self.bonus_keywords.items():
            if re.search(r"\b" + re.escape(kw.upper()) + r"\b", t_upper):
                content_score += points

        # Anchor word bonus
        for aw in self.anchor_words:
            if re.search(r"\b" + re.escape(aw) + r"\b", t_upper):
                content_score += self.anchor_word_weight

        # V28: Configurable Billion-Scale Detection
        if self.billion_regex.search(t_upper):
            content_score += self.billion_scale_bonus

        # V27: Cluster Bonus - multiplicative boost when 2+ high-signal terms co-occur
        cluster_hits = sum(
            1 for term in self.cluster_terms if re.search(r"\b" + re.escape(term) + r"\b", t_upper)
        )
        if cluster_hits >= 2:
            content_score = content_score * self.cluster_multiplier

        # V28: Untrusted Aggregator Check
        if content_score == 0:
            if any(agg in source_name for agg in self.untrusted_aggregators):
                return (self.relevance_floor_penalty, base_weight)

        return (round(content_score, 1), base_weight)

    def _update_velocity_pulse(self, title, now_ts):
        """V24.2 SVM: Tracks frequency of keywords to identify velocity shifts."""
        t_upper = title.upper()
        for kw in self.priority_keywords:
            if kw in t_upper:
                if kw not in self.velocity_pulse:
                    self.velocity_pulse[kw] = []
                self.velocity_pulse[kw].append(now_ts)

        for tick in self.priority_tickers:
            if re.search(rf"\b{tick}\b", t_upper):
                if tick not in self.velocity_pulse:
                    self.velocity_pulse[tick] = []
                self.velocity_pulse[tick].append(now_ts)

    def _finalize_velocity_metrics(self):
        """Calculates deltas (velocity) for monitored keywords over the last 4h vs prior 24h."""
        now = time.time()
        metrics = {}
        for kw, timestamps in self.velocity_pulse.items():
            # Clean old timestamps (> 24h)
            valid = [ts for ts in timestamps if (now - ts) < 86400]
            self.velocity_pulse[kw] = valid

            recent_4h = [ts for ts in valid if (now - ts) < 14400]
            prior_20h = [ts for ts in valid if 14400 <= (now - ts) < 86400]

            # Simple Velocity: Frequency ratio
            v_score = len(recent_4h) / (len(prior_20h) / 5 + 1)  # Normalized
            metrics[kw] = {
                "count_24h": len(valid),
                "count_4h": len(recent_4h),
                "velocity": round(v_score, 2),
            }

        try:
            with open(VELOCITY_PULSE_DB, "w", encoding="utf-8") as f:
                json.dump({"timestamp": now, "metrics": metrics}, f, indent=4)
        except:
            pass
        return metrics

    async def fetch_ticker_news(self, tickers, macro_headlines=None):
        """
        V30.4: Specialized Ticker-Specific Intelligence Harvest.
        1. Scans existing macro headlines for ticker mentions.
        2. Performs surgical RSS fetch for tickers with 0 news.
        3. ENFORCES strict safety and freshness gates on every item.
        """
        ticker_news_pool = []
        ticker_status = {t: 0 for t in tickers}
        macro_headlines = macro_headlines or []
        now_ts = time.time()

        # Pass 1: Scan macro headlines
        for res in macro_headlines:
            raw_title = res.get("title", "").upper()
            for t in tickers:
                if f" {t} " in f" {raw_title} " or f"${t}" in raw_title:
                    ticker_news_pool.append(res)
                    ticker_status[t] += 1

        # Pass 2: Surgical Search for under-represented tickers
        for t in tickers:
            if ticker_status[t] == 0:
                try:
                    q = f"${t} stock news"
                    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=en-US&gl=US&ceid=US:en"
                    # V30.4: Surgical Fetch with 2026-grade async handling
                    feed = await asyncio.to_thread(feedparser.parse, url)

                    for entry in feed.entries[:3]:
                        # V30.4: CRITICAL - Freshness Gate Enforcement
                        pub_ts = now_ts
                        if hasattr(entry, "published_parsed") and entry.published_parsed:
                            pub_ts = time.mktime(entry.published_parsed)

                        if not self.is_fresh_enough(pub_ts):
                            log.debug(f"  [REJECT-STALE] {t}: {entry.title[:45]}...")
                            continue  # REJECT STALE NEWS

                        res = {
                            "title": entry.title,
                            "link": entry.link,
                            "source": entry.get("source", {}).get("title", "Google News"),
                            "display_source": entry.get("source", {}).get("title", "Google News"),
                            "date": pub_ts,
                            "timestamp": pub_ts,
                            "score": self.score_headline(entry.title, "Google News")[0],
                        }

                        if self.is_article_safe(res["title"], res["link"], res["source"]):
                            ticker_news_pool.append(res)
                            ticker_status[t] += 1
                except Exception as e:
                    log.error(f"  [ERR] Ticker Fetch Failed ({t}): {e}")
                    continue

        return ticker_news_pool

    async def fetch_agg(self):
        """Aggregates and scores news with hardening/stealth protocols."""
        print(f"[DEBUG] fetch_agg called. Cache target: {MACRO_NEWS_CACHE}")
        # V23.61: 15-minute Cache Enforcement
        if MACRO_NEWS_CACHE.exists():
            try:
                with open(MACRO_NEWS_CACHE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    cached_at = cache_data.get("timestamp", 0)
                    elapsed = time.time() - cached_at
                    if elapsed < 900:  # 15 minutes
                        ttl = int(900 - elapsed)
                        log.info(
                            f"[CACHE] Macro News Fresh: {ttl}s remaining. Serving {len(cache_data.get('headlines', []))} ranked items."
                        )
                        return cache_data.get("headlines", [])
                    else:
                        log.info(
                            f"[CACHE] Macro News EXPIRED ({int(elapsed)}s old). Triggering fresh aggregate..."
                        )
            except Exception as e:
                log.warning(f"[CACHE] Read failure: {e}")

        log.info("[MACRO] Aggregating multi-source news feeds...")
        all_items = []
        prices = self._load_prices()

        # V23.60: Use centralized stealth auth for fingerprint matching
        try:
            from yahoo_auth import get_valid_auth

            _, _, user_agent = await get_valid_auth()
        except:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

        # V23.91: Strict Cross-Source Deduplication
        seen_titles = set()

        async with AsyncSession(impersonate="chrome146") as client:
            client.headers.update(
                {
                    "User-Agent": user_agent,
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                }
            )

            # V23.79: Parallelize across domains, sequential jitter within domains
            domain_queues = {}
            for name, cfg in self.feeds.items():
                url = cfg["url"]
                domain = urllib.parse.urlparse(url).netloc
                if domain not in domain_queues:
                    domain_queues[domain] = []
                domain_queues[domain].append((name, cfg))

            async def process_queue(domain, queue):
                queue_items = []
                for i, (name, cfg) in enumerate(queue):
                    url = cfg["url"]
                    f_type = cfg["type"]
                    try:
                        # Jitter ONLY within the same domain (V23.79 Optimization)
                        if i > 0:
                            delay = random.uniform(2.5, 7.0)
                            log.info(
                                f"  [STEALTH] Cadence Match ({domain}): Sleeping {delay:.2f}s..."
                            )
                            await asyncio.sleep(delay)

                        log.info(f"  [FETCH] {name} ({f_type.upper()}) -> {url}")

                        # V24.2: Robust Fetch with Retry & Impersonation Rotation
                        res = None
                        impersonations = [
                            "chrome110",
                            "chrome120",
                            "chrome124",
                            "edge101",
                            "safari_ios_16_5",
                        ]

                        for attempt in range(3):
                            try:
                                current_imp = impersonations[attempt % len(impersonations)]
                                # Apply Paywall Bypass Headers
                                fetch_headers = PaywallIntelligence.apply_stealth_headers(
                                    url, client.headers.copy()
                                )
                                res = await client.get(
                                    url, timeout=15, impersonate=current_imp, headers=fetch_headers
                                )
                                if res.status_code == 200:
                                    break
                                log.warning(
                                    f"  [!] Attempt {attempt+1} failed ({res.status_code}) for {name}. Retrying with {current_imp}..."
                                )
                                await asyncio.sleep(random.uniform(2, 5))
                            except Exception as e:
                                log.error(f"  [!] Fetch error {name} (Attempt {attempt+1}): {e}")
                                await asyncio.sleep(2)

                        if not res or res.status_code != 200:
                            status = res.status_code if res else "TIMEOUT"
                            log.error(f"  [!] Blocked or Error {name}: HTTP {status}")
                            continue

                        now_ts = time.time()
                        source_item_count = 0

                        if f_type == "rss":
                            feed = feedparser.parse(res.content)
                            for entry in feed.entries:
                                title = entry.get("title", "No Title").strip()

                                # V28: Hardened Deduplication (Jaccard-lite + Entity Intersection)
                                tokens = frozenset(re.findall(r"\b\w{4,}\b", title.lower()))
                                entities = frozenset(re.findall(r"\b[A-Z][A-Za-z]{3,}\b", title))

                                is_dup = False
                                for st, se in seen_titles:
                                    # 1. Jaccard Overlap (General logic)
                                    overlap = len(tokens & st) / (len(tokens | st) + 1)
                                    if overlap > 0.4:
                                        is_dup = True
                                        break

                                    # 2. Entity Intersection (High-signal subjects like 'Aeluma')
                                    # If they share a proper noun and any other word, they are likely duplicates.
                                    common_entities = entities & se
                                    if common_entities:
                                        if len(tokens & st) >= 2:
                                            is_dup = True
                                            break

                                if is_dup:
                                    continue
                                seen_titles.add((tokens, entities))

                                link = entry.get("link", "")
                                pub_date = entry.get("published", "")

                                # V25.5: Google News RSS publisher extraction (title key)
                                display_source = name
                                if (
                                    "news.google.com" in name.lower()
                                    or "google news" in name.lower()
                                ):
                                    gn_src = entry.get("source", {})
                                    if isinstance(gn_src, dict):
                                        display_source = gn_src.get("title", name)
                                    elif isinstance(gn_src, str):
                                        display_source = gn_src
                                    # Also strip " - Publisher" suffix from title if present
                                    # e.g. "Stock market falls — Reuters" -> keep as-is, tag it

                                entry_ts = now_ts
                                if hasattr(entry, "published_parsed") and entry.published_parsed:
                                    entry_ts = time.mktime(entry.published_parsed)

                                summary = entry.get("summary", entry.get("description", ""))
                                summary = re.sub(r"<[^>]+>", "", summary).strip()

                                # V26.10: News Hardening Gate Integration
                                final_link = await self.resolve_redirect(link, session=client)
                                if not self.is_article_safe(
                                    title, final_link, display_source, summary, name
                                ):
                                    continue

                                # V24.2: Signal Decay Engine (5% per hour after 1h, floor at 50%)
                                # V26.10 Hardening: 24h Decay Gate + 36h Hard Limit
                                # Top Hierarchy: SEMI articles can go back 2 weeks
                                is_semi_feed = cfg.get("is_semi", False)
                                if not self.is_fresh_enough(entry_ts, is_semi=is_semi_feed):
                                    continue

                                content_score, base_weight = self.score_headline(title, name)
                                base_weight = self.apply_freshness_decay(
                                    base_weight, entry_ts, is_semi=is_semi_feed
                                )

                                # Flag Earnings (V24.1)
                                is_earnings = "EARNINGS" in title.upper() or name == "CNBC Earnings"
                                if is_earnings:
                                    content_score += 100  # Boost earnings

                                # V28: DEPRECATED enrichment here to prevent Double-Enrichment HTML corruption
                                # The UI/Email layer (email_market_synopsis.py) handles flair injection.
                                enriched_title = title

                                summary = re.sub(
                                    r"(?i)[T]?he post .*? appeared first on .*?(?:\.|$)",
                                    "",
                                    summary,
                                ).strip()
                                summary = re.sub(
                                    r"(?i)Read more on Yahoo Finance.*", "", summary
                                ).strip()

                                # V24.2: Sentiment Velocity Monitor (SVM) Update
                                self._update_velocity_pulse(title, now_ts)

                                queue_items.append(
                                    {
                                        "title": enriched_title,
                                        "raw_title": title,
                                        "summary": summary,
                                        "link": final_link,
                                        "source": name,
                                        "display_source": self.normalize_source(display_source),
                                        "base_weight": round(base_weight, 1),
                                        "content_score": round(content_score, 1),
                                        "score": round(
                                            base_weight + content_score, 1
                                        ),  # Legacy total
                                        "date": pub_date,
                                        "is_earnings": is_earnings,
                                        "is_earn": is_earnings,
                                        "is_semi": is_semi_feed,
                                    }
                                )
                                source_item_count += 1
                        else:
                            # Scrape Type
                            from bs4 import BeautifulSoup

                            soup = BeautifulSoup(res.content, "html.parser")

                            items = []
                            if "bloomberg" in url:
                                links = soup.find_all(
                                    "a",
                                    href=re.compile(r"/news/articles/|/news/features/"),
                                )
                                for link in links[:10]:
                                    title = link.get_text().strip()
                                    if len(title) < 20:
                                        continue
                                    items.append(
                                        {
                                            "title": title,
                                            "link": (
                                                "https://www.bloomberg.com" + link["href"]
                                                if link["href"].startswith("/")
                                                else link["href"]
                                            ),
                                        }
                                    )
                            elif "thefly" in url:
                                links = soup.find_all("a", class_="newsTitleLink")
                                for link in links[:10]:
                                    title = link.get_text().strip()
                                    items.append(
                                        {
                                            "title": title,
                                            "link": (
                                                "https://thefly.com" + link["href"]
                                                if link["href"].startswith("/")
                                                else link["href"]
                                            ),
                                        }
                                    )
                            elif "yahoo" in url:
                                # V25.4: Hardened Yahoo scraper — filter nav junk
                                # Yahoo Finance topic pages mix real article <a> tags with
                                # site-nav links. We filter by: min length, not-junk-title,
                                # and must contain at least one uppercase word (real headline).
                                links = soup.find_all("a", href=True)
                                for link in links:
                                    title = link.get_text().strip()
                                    href = link.get("href", "")
                                    if len(title) < 30:
                                        continue  # too short = nav item
                                    if title.lower() in self.SCRAPE_JUNK_TITLES:
                                        continue
                                    if not re.search(r"[A-Z]", title):
                                        continue  # no caps = nav
                                    if not (
                                        "/news/" in href or "/m/" in href or "finance.yahoo" in href
                                    ):
                                        continue
                                    full_href = (
                                        href
                                        if href.startswith("http")
                                        else "https://finance.yahoo.com" + href
                                    )
                                    items.append({"title": title, "link": full_href})
                                    if len(items) >= 15:
                                        break
                            elif "zerohedge.com" in url:
                                # V28: Surgical ZH Category Scraper
                                # Targets specific article headers in Markets/Tech/Energy/Econ
                                headers = soup.find_all("h2")
                                for h in headers:
                                    a_tag = h.find("a", href=True)
                                    if not a_tag:
                                        continue
                                    title = a_tag.get_text().strip()
                                    href = a_tag["href"]
                                    if len(title) < 25:
                                        continue
                                    # Ensure link is absolute
                                    full_href = (
                                        href
                                        if href.startswith("http")
                                        else "https://www.zerohedge.com" + href
                                    )

                                    # V28: Surgical ZH Category Scraper Hardening
                                    # Skip 'PREMIUM' paywalled articles by checking title and parent container
                                    if "PREMIUM" in title.upper():
                                        continue

                                    article_container = h.find_parent(
                                        "div", class_=re.compile(r"Article_article")
                                    )
                                    if (
                                        article_container
                                        and "PREMIUM" in article_container.get_text().upper()
                                    ):
                                        continue

                                    items.append({"title": title, "link": full_href})
                                    if len(items) >= 12:
                                        break

                            for it in items:
                                title = it["title"]
                                # V28: Hardened Deduplication (Jaccard-lite + Entity Intersection)
                                tokens = frozenset(re.findall(r"\b\w{4,}\b", title.lower()))
                                entities = frozenset(re.findall(r"\b[A-Z][A-Za-z]{3,}\b", title))

                                is_dup = False
                                for st, se in seen_titles:
                                    # 1. Jaccard Overlap
                                    overlap = len(tokens & st) / (len(tokens | st) + 1)
                                    if overlap > 0.4:
                                        is_dup = True
                                        break

                                    # 2. Entity Intersection
                                    common_entities = entities & se
                                    if common_entities:
                                        if len(tokens & st) >= 2:
                                            is_dup = True
                                            break

                                if is_dup:
                                    continue
                                seen_titles.add((tokens, entities))

                                # V26.10: Scrape Gate Integration
                                if not self.is_article_safe(
                                    title, it["link"], name, feed_name=name
                                ):
                                    continue

                                content_score, base_weight = self.score_headline(title, name)

                                # Flag Earnings (V24.1)
                                is_earnings = "EARNINGS" in title.upper() or name == "CNBC Earnings"
                                if is_earnings:
                                    content_score += 100  # Boost earnings

                                enriched_title = title

                                # V24.2: SVM Update
                                self._update_velocity_pulse(title, now_ts)

                                queue_items.append(
                                    {
                                        "title": enriched_title,
                                        "raw_title": title,
                                        "summary": "",
                                        "link": it["link"],
                                        "source": name,
                                        "display_source": self.normalize_source(name),
                                        "base_weight": round(base_weight, 1),
                                        "content_score": round(content_score, 1),
                                        "score": round(base_weight + content_score, 1),
                                        "date": "Just now",
                                        "is_earnings": is_earnings,
                                    }
                                )
                                source_item_count += 1

                        log.info(f"  [SUCCESS] {name}: {source_item_count} items identified.")
                    except Exception as e:
                        log.error(f"  [ERR] Failed {name}: {e}")
                return queue_items

            # Execute all domain groups in parallel
            tasks = [process_queue(domain, q) for domain, q in domain_queues.items()]
            results_batches = await asyncio.gather(*tasks)
            for batch in results_batches:
                all_items.extend(batch)

        # V24.1: Dynamic List Extension for Earnings News
        has_earnings = any(it.get("is_earnings") for it in all_items)

        log.info(
            f"[DEBUG] Aggregator: Pulled {len(all_items)} valid raw items before scoring sort."
        )

        # V25.4: Source Diversity Cap — enforce MAX_PER_SOURCE per ROOT DOMAIN (not feed name).
        # We bucket by the actual display_source domain, not the feed name, so Google News
        # articles from Reuters count toward 'reuters.com', not 'google'.
        import urllib.parse as _up

        def _src_bucket(item):
            ds = item.get("display_source", item.get("source", "unknown"))
            # V25.6: Enhanced Bucketing
            if ds.startswith("http"):
                return _up.urlparse(ds).netloc.lower().replace("www.", "")

            clean = re.sub(r"[^a-zA-Z0-9]", "", ds).lower()
            if "motleyfool" in clean:
                return "BLACKLIST"
            if "cnbc" in clean:
                return "cnbc"
            if "google" in clean:
                return "google"
            if "yahoo" in clean:
                return "yahoo"
            if "wsj" in clean:
                return "wsj"
            if "reuters" in clean:
                return "reuters"
            if "bloomberg" in clean:
                return "bloomberg"
            if "financialtimes" in clean or "ft" in clean:
                return "ft"
            if "barrons" in clean:
                return "barrons"
            if "investorsbusiness" in clean or "ibd" in clean:
                return "ibd"
            if "marketwatch" in clean:
                return "marketwatch"
            if "seekingalpha" in clean:
                return "seekingalpha"
            if "oilprice" in clean:
                return "oilprice"
            if "zerohedge" in clean:
                return "zerohedge"
            if "msn" in clean:
                return "msn"
            return clean[:10]

        all_sorted = sorted(all_items, key=lambda x: x["score"], reverse=True)
        source_counts = {}
        top_ranked = []
        for item in all_sorted:
            src_key = _src_bucket(item)
            if src_key == "BLACKLIST":
                continue
            count = source_counts.get(src_key, 0)
            if count >= self.MAX_PER_SOURCE:
                log.debug(
                    f"  [SOURCE-CAP] Skipping — {src_key} at {count}/{self.MAX_PER_SOURCE}: {item['raw_title'][:55]}"
                )
                continue
            source_counts[src_key] = count + 1
            top_ranked.append(item)

        diversity = {k: v for k, v in sorted(source_counts.items(), key=lambda x: -x[1])}
        log.info(f"[V25.4] Source Diversity After Cap: {diversity}")
        log.info(
            f"[V25.4] Total viable articles after cap: {len(top_ranked)} (from {len(all_items)} raw)"
        )

        # Save to Cache
        try:
            with open(MACRO_NEWS_CACHE, "w", encoding="utf-8") as f:
                json.dump({"timestamp": time.time(), "headlines": top_ranked}, f, indent=4)
        except:
            pass

        # V24.2: Finalize Sentiment Velocity Metrics (SVM)
        self._finalize_velocity_metrics()

        log.info(
            f"[MACRO] Aggregation complete. {len(top_ranked)} high-alpha headlines passed to NLP (Earnings Boost: {has_earnings})."
        )
        return top_ranked


if __name__ == "__main__":

    async def test():
        agg = MacroAggregator()
        results = await agg.fetch_agg()
        for i, res in enumerate(results):
            try:
                print(f"{i+1}. [{res['score']}] {res['title']}")
            except:
                print(f"{i+1}. [{res['score']}] {res['title'].encode('ascii', 'ignore').decode()}")

    asyncio.run(test())
