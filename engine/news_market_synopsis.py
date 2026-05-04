# V30.4: GIGACPO SOVEREIGN NEWS INTELLIGENCE ENGINE (MIRROR EDITION)
import argparse
import asyncio
import datetime
import json
import logging
import os
import random
import re
import smtplib
import sys
import time

import requests

# V28: Hierarchy Leader Error Monitoring
try:
    import error_monitor
except ImportError:
    from engine import error_monitor
error_monitor.init_error_monitor()

try:
    from ticker_utils import (
        MAJOR_SEMI_TICKERS,
        VERSION,
        format_news_date,
        get_display_symbol,
        get_header_timestamp,
        is_semi_article,
    )
except ImportError:
    from engine.ticker_utils import (
        MAJOR_SEMI_TICKERS,
        VERSION,
        format_news_date,
        get_display_symbol,
        get_header_timestamp,
        is_semi_article,
    )

import hashlib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from curl_cffi import requests as cffi_requests
from dotenv import load_dotenv

# V28: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
    error_monitor.init_error_monitor()
except SystemExit:
    raise  # Let the dependency manager cleanly exit the process
except Exception as e:
    print(f"[!] Dependency Guardian Warning: {e}")

# Engine Foundations
try:
    from live_blog_scraper import LiveBlogScraper
    from live_prices import async_run_fetch
    from local_nlp import LocalIntelligenceSynthesizer
    from macro_aggregator import MacroAggregator
    from market_session import MarketSession
    from paywall_guardian import PaywallGuardian
    from paywall_intelligence import DeepScraper, PaywallIntelligence
    from remote_sync import RemoteSync
except ImportError:
    from engine.email_spark_fetcher import run_spark_fetch
    from engine.live_blog_scraper import LiveBlogScraper
    from engine.live_prices import async_run_fetch
    from engine.local_nlp import LocalIntelligenceSynthesizer
    from engine.macro_aggregator import MacroAggregator
    from engine.market_session import MarketSession
    from engine.paywall_guardian import PaywallGuardian
    from engine.paywall_intelligence import DeepScraper, PaywallIntelligence
    from engine.remote_sync import RemoteSync

# V28: Authoritative Theme Provider
try:
    from theme_provider import theme
except ImportError:
    from engine.theme_provider import theme

try:
    from market_synopsis_scraper import MarketSynopsisScraper
except ImportError:
    from engine.market_synopsis_scraper import MarketSynopsisScraper

try:
    from synopsis_archive import SynopsisArchiveManager
except ImportError:
    from engine.synopsis_archive import SynopsisArchiveManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)
load_dotenv()


class NewsMarketSynopsisEngine:
    """
    GIGACPO SOVEREIGN NEWS INTELLIGENCE V30.4 (MIRROR MODE)
    Literally the Email engine but stripped for news-only portal access.
    """

    def __init__(self):
        def ts():
            return datetime.datetime.now().strftime("%H:%M:%S")

        print(f"[{ts()}] [DEBUG] Constructor: Setting paths...")
        self.root = Path(__file__).parent.parent
        self.db_path = self.root / "database"
        self.web_root = self.root / "web"

        self.now = self._get_est_now()

        # Design Tokens (Synced with Theme Provider)
        self.COLOR_BG = theme.get_color("bg_main", "#020617")
        self.COLOR_CARD = theme.get_color("bg_surface", "#0f172a")
        self.COLOR_ACCENT = theme.get_color("bg_accent", "#1e293b")
        self.COLOR_DEEP = theme.get_color("bg_deep", "#0a0f1e")
        self.COLOR_TEXT = theme.get_color("text_bright", "#f8fafc")
        self.COLOR_DIM = theme.get_color("text_dim", "#64748b")
        self.COLOR_GOLD = theme.get_color("gold", "#f59e0b")
        self.COLOR_INDIGO = theme.get_color("indigo", "#6366f1")
        self.COLOR_GREEN = theme.get_color("green", "#10b981")
        self.COLOR_DANGER = theme.get_color("danger", "#f43f5e")
        self.COLOR_BLUE = theme.get_color("blue", "#38bdf8")

        self.ticker_name_map = self._load_json("ticker_name_map.json")
        self.market_session = MarketSession()
        self.watchlist = self._load_watchlist()
        self.synopsis_scraper = MarketSynopsisScraper()
        self.archive_mgr = SynopsisArchiveManager(self.root)

    def _load_watchlist(self, custom_path=None):
        watchlist = []
        path = Path(custom_path) if custom_path else self.root / "tickers.txt"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    raw = content.replace("\n", ",").replace(" ", ",")
                    watchlist = [t.strip().upper() for t in raw.split(",") if t.strip()]
            except Exception as e:
                print(f"[WARN] Failed to load authoritative watchlist: {e}")
        return watchlist

    def _get_est_now(self):
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        try:
            from zoneinfo import ZoneInfo

            return now_utc.astimezone(ZoneInfo("US/Eastern"))
        except:
            return now_utc - datetime.timedelta(hours=4)

    def is_legit_ticker(self, t):
        if not t or not isinstance(t, str):
            return False
        t = t.upper()
        if len(t) < 2 or t.isdigit():
            return False
        if any(x in t for x in [" ", "/", "\\", "(", ")", ",", ":", "'", '"']):
            return False
        return True

    def _load_json(self, name):
        p = self.db_path / name
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def get_market_session(self, symbol=None, dt_override=None):
        label = self.market_session.get_market_session_label(symbol, dt_override)
        return label if label != "CLOSED" else ""

    def get_session_data(self, p_data, symbol=None):
        sess = self.get_market_session(symbol)
        effective_sess = sess
        price = p_data.get("price", 0)
        pct = p_data.get("change_pct", 0)
        ext_type = p_data.get("ext_type")
        if ext_type and ext_type in ["OVN", "PRE", "POST", "AH"]:
            match = ext_type == sess
            if not match:
                match = (
                    (sess == "AH" and ext_type in ["POST", "AH"])
                    or (sess == "PRE" and ext_type == "PRE")
                    or (sess == "OVN" and ext_type in ["POST", "AH", "OVN"])
                )
            if not match and sess == "PRE" and ext_type == "OVN":
                match = True
            if match:
                e_p = p_data.get("ext_price")
                e_pct = p_data.get("ext_pct")
                if e_p is not None:
                    price = e_p
                    prev = p_data.get("close_price") or p_data.get("prev_close")
                    if prev:
                        pct = ((price / prev) - 1) * 100
                    elif e_pct is not None:
                        pct = e_pct
                    lbl = ext_type
                    if lbl == "POST":
                        lbl = "AH"
                    effective_sess = lbl
            elif sess == "LIVE":
                effective_sess = "LIVE"
            else:
                effective_sess = "CLOSED"
        return price, pct, effective_sess

    def get_session_tag_html(self, fs="8px", sess_override=None, color=None):
        sess = sess_override if sess_override else ""
        if not sess:
            return ""
        if sess == "PM":
            sess = "PRE"
        if sess == "POST":
            sess = "AH"
        base_style = f"padding:1px 3px; border-radius:3px; font-weight:bold; margin-left:4px; vertical-align:middle; display:inline-block; font-size:{fs}; font-family:monospace !important;"
        if sess == "LIVE":
            return f'<span style="{base_style} color:#10b981; background-color:#064e3b; border:1px solid #10b981;">L<span style="color:#10b981;">⚡</span></span>'
        colors = {
            "PRE": ("#f59e0b", "#451a03"),
            "AH": ("#ef4444", "#450a0a"),
            "OVN": ("#f59e0b", "#451a03"),
            "CLOSED": ("#94a3b8", "#1e293b"),
        }
        c, bg = colors.get(sess, ("#94a3b8", "#1e293b"))
        return f'<span style="{base_style} color:{c}; background-color:{bg}; border:1px solid {c}40;">{sess}</span>'

    def inject_price_flair(self, text, prices, master=None, link=True):
        if not text:
            return text
        words = text.split()
        for i, word in enumerate(words):
            stripped = word.strip(".,;:()$ '\"?!")
            if not stripped:
                continue
            clean_word = stripped.upper()
            if clean_word in prices and self.is_legit_ticker(clean_word):
                p_data = prices[clean_word]
                price, pct, sess = self.get_session_data(p_data, clean_word)
                if price is None or pct is None:
                    continue
                color = "#22c55e" if pct >= 0 else "#ef4444"
                sign = "+" if pct >= 0 else ""
                sess_tag = self.get_session_tag_html(fs="8px", sess_override=sess)
                anchor = ""
                if sess in ["PRE", "AH", "OVN", "POST"]:
                    c_p = p_data.get("close_price") or p_data.get("price")
                    if c_p:
                        anchor = f' <span style="font-size:8px; color:#94a3b8; font-weight:normal;">| C: ${c_p:,.2f}</span>'
                start_idx = word.find(stripped)
                prefix = word[:start_idx].replace("'", "").replace('"', "").replace("`", "")
                suffix = (
                    word[start_idx + len(stripped) :]
                    .replace("'", "")
                    .replace('"', "")
                    .replace("`", "")
                )
                flair = f'{prefix}<strong>{stripped}</strong>&nbsp;(<span style="color:{color}; font-weight:bold;">${price:,.2f}&nbsp;{sign}{pct:.1f}%{sess_tag}{anchor}</span>){suffix}'
                words[i] = flair
                # V30.4.7: Fixed bug where it returned after first match. Continue to find all tickers.
        return " ".join(words)

    def _get_session_badge(self, s_type):
        try:
            from ticker_utils import get_session_badge_style
        except ImportError:
            from engine.ticker_utils import get_session_badge_style
        return get_session_badge_style(s_type)

    def _render_valuation_row(self, item):
        m_cap = item.get("marketCap") or item.get("market_cap")
        pe = item.get("trailingPE") or item.get("pe")
        pe26 = item.get("pe26")
        pe27 = item.get("pe27")
        rev = item.get("revenueGrowth") or item.get("rev")
        if not any([m_cap, pe, pe26, pe27, rev]):
            return ""
        parts = []
        if m_cap:
            if m_cap >= 1e12:
                cap_str = f"${m_cap/1e12:.2f}T"
            elif m_cap >= 1e9:
                cap_str = f"${m_cap/1e9:.1f}B"
            else:
                cap_str = f"${m_cap/1e6:.1f}M"
            parts.append(f"MCap: {cap_str}")
        if pe26 or pe27:
            if pe26:
                parts.append(f"'26 [{pe26:.1f}]")
            if pe27:
                parts.append(f"'27 [{pe27:.1f}]")
        elif pe:
            parts.append(f"P/E: {pe:.1f}x")
        if rev:
            rev_str = (
                f"{rev*100:+.1f}%"
                if isinstance(rev, float) and abs(rev) < 10
                else f"${rev/1e6:.1f}M"
            )
            parts.append(f"Rev: {rev_str}")
        content = "  ".join(parts)
        return f'<div class="tk-val">[ {content} ]</div>'

    async def gather_all_data(self, custom_tickers=None, force=False):
        agg = MacroAggregator()
        macro_headlines = await agg.fetch_agg()
        nlp = LocalIntelligenceSynthesizer()

        # Fresh news rotation
        sent_news_path = Path("database/sent_news_history.json")
        sent_news_history = {}
        if sent_news_path.exists():
            try:
                with open(sent_news_path, "r", encoding="utf-8") as f:
                    sent_news_history = json.load(f)
            except:
                pass

        prices = self._load_json("live_prices.json")
        master = self._load_json("CPO_MASTER_DATA.json")
        synopsis_data = await self.synopsis_scraper.fetch_synopsis(self.get_market_session())

        # Categorization logic
        semi_sources = [
            "SemiAnalysis",
            "SemiEngineering",
            "Semiconductor Today",
            "EE Times Semi",
            "Semiconductor Digest",
            "SemiWiki",
            "IEEE Spectrum Semi",
            "Google News CPO Photonics",
            "Google News Semiconductors",
            "Google News Transceiver",
        ]

        # Intel generation
        m_fg = 50  # Default
        vibe_status = "NEUTRAL"
        intel_text, used_links = nlp.synthesize_market_narrative(macro_headlines, vibe_status)

        # V30.4.7: Authoritative Ticker Intelligence Gateway (Hierarchical)
        # Replaces manual feedparser loop with a centralized, safety-gated engine.
        ticker_news_pool = await agg.fetch_ticker_news(self.watchlist, macro_headlines)

        # V30.4.7: Forward P/E & Valuation Hydration (Mirror Mandate)
        try:
            from ticker_utils import extract_ticker_eps
        except ImportError:
            from engine.ticker_utils import extract_ticker_eps

        watchlist_data = []
        for t in self.watchlist:
            p_data = prices.get(t, {})
            # Hydrate forward estimates
            eps26, eps27 = extract_ticker_eps(master, t)
            price = p_data.get("price", 0)
            p_data["pe26"] = price / eps26 if price and eps26 and eps26 > 0 else None
            p_data["pe27"] = price / eps27 if price and eps27 and eps27 > 0 else None

            price, pct, sess = self.get_session_data(p_data, t)
            watchlist_data.append(
                {
                    "symbol": t,
                    "price": price,
                    "pct": pct,
                    "sess": sess,
                    "market_cap": p_data.get("market_cap") or p_data.get("marketCap"),
                    "pe": p_data.get("pe") or p_data.get("trailingPE"),
                    "pe26": p_data["pe26"],
                    "pe27": p_data["pe27"],
                    "rev": p_data.get("rev") or p_data.get("revenueGrowth"),
                    "notes": master.get(t, {}).get("human_research", {}).get("Notes", ""),
                }
            )

        # V30.4.7: Hierarchy Sorting Protocol (L > PRE > AH > OVN > CLOSED)
        sess_priority = {"LIVE": 0, "PRE": 1, "AH": 2, "OVN": 3, "CLOSED": 4}
        watchlist_data.sort(key=lambda x: (sess_priority.get(x["sess"], 99), -x["pct"]))

        return {
            "headlines": macro_headlines,
            "prices": prices,
            "synopsis": synopsis_data,
            "intel_text": intel_text,
            "used_links": used_links,
            "history": sent_news_history,
            "watchlist_data": watchlist_data,
            "ticker_news_pool": ticker_news_pool,
        }

    async def compose_html(self, data):
        prices = data["prices"]
        headlines = data["headlines"]
        synopsis_data = data["synopsis"]
        intel_text = data["intel_text"]
        used_links = data["used_links"]
        sent_news_history = data["history"]
        watchlist_data = data["watchlist_data"]
        ticker_news_pool = data.get("ticker_news_pool", [])
        now_ts = time.time()

        bg_main = "#020617"
        bg_surface = "#0f172a"
        bg_accent = "#1e293b"
        bg_deep = "#0a0f1e"
        text_bright = "#f8fafc"
        text_dim = "#64748b"
        gold = "#f59e0b"
        indigo = "#6366f1"
        bull = "#10b981"
        bear = "#f43f5e"
        accent = "#38bdf8"
        font_family = "monospace, sans-serif"

        macro_intel_rows = ""
        earnings_intel_rows = ""
        semi_trade_rows = ""
        row_count = 0
        earn_count = 0
        semi_count = 0
        # V30.4.9: Decentralized to ticker_utils (Hierarchy Leader)
        # semi_sources list removed locally to ensure modular parity.

        ticker_tracker = {t: [] for t in self.watchlist}
        seen_links = set()

        # V30.4.9: Authoritative Multi-Source Ticker Tracking
        # Merges macro headlines with surgical ticker harvest
        all_potential_ticker_news = ticker_news_pool + headlines

        for res in all_potential_ticker_news:
            link = res.get("link")
            if not link or link in seen_links:
                continue

            raw_title = res.get("title", "").upper()
            for t in self.watchlist:
                if f" {t} " in f" {raw_title} " or f"${t}" in raw_title:
                    ticker_tracker[t].append(res)
                    seen_links.add(link)
                    break  # Assign to first matching ticker to avoid section bloat

        ticker_news_rows = ""
        ticker_news_count = 0
        used_links_ticker = set()
        for t in self.watchlist:
            if ticker_tracker[t]:
                res = ticker_tracker[t][0]
                if res["link"] not in used_links_ticker:
                    row_bg = "#0f172a" if ticker_news_count % 2 == 0 else "#020617"
                    cleaned_title = (
                        re.sub(r"\s+[-|•|–]\s+.*$", "", res.get("title", ""))
                        .strip()
                        .replace("📊", "»")
                    )
                    f_title = self.inject_price_flair(cleaned_title, prices)
                    src_label = res.get("display_source", res.get("source", ""))[:22]
                    pub_date = format_news_date(res.get("date") or res.get("timestamp"))
                    DATE_STR = (
                        f'<span style="font-size:10px; color:{self.COLOR_DIM}; margin-left:8px;">{pub_date}</span>'
                        if pub_date
                        else ""
                    )
                    SRC_BADGE = f'&nbsp;<span class="src-badge">[{src_label}]</span>{DATE_STR}'
                    ticker_news_rows += f'<div style="background-color:{row_bg}; padding:10px 14px; margin-bottom:6px; border-radius:4px; border-left:3px solid {accent}; color:{text_bright};"><span style="font-size:14px; color:{accent};">◈</span>&nbsp;<a href="{res["link"]}" class="news-link">{f_title}</a>{SRC_BADGE}</div>'
                    ticker_news_count += 1
                    used_links_ticker.add(res["link"])

        for t in self.watchlist:
            if ticker_news_count < 15 and len(ticker_tracker[t]) > 1:
                res = ticker_tracker[t][1]
                if res["link"] not in used_links_ticker:
                    row_bg = "#0f172a" if ticker_news_count % 2 == 0 else "#020617"
                    cleaned_title = (
                        re.sub(r"\s+[-|•|–]\s+.*$", "", res.get("title", ""))
                        .strip()
                        .replace("📊", "»")
                    )
                    f_title = self.inject_price_flair(cleaned_title, prices)
                    src_label = res.get("display_source", res.get("source", ""))[:22]
                    pub_date = format_news_date(res.get("date") or res.get("timestamp"))
                    DATE_STR = (
                        f'<span style="font-size:10px; color:{self.COLOR_DIM}; margin-left:8px;">{pub_date}</span>'
                        if pub_date
                        else ""
                    )
                    SRC_BADGE = f'&nbsp;<span class="src-badge">[{src_label}]</span>{DATE_STR}'
                    ticker_news_rows += f'<div style="background-color:{row_bg}; padding:10px 14px; margin-bottom:6px; border-radius:4px; border-left:3px solid {accent}; color:{text_bright};"><span style="font-size:14px; color:{accent};">◈</span>&nbsp;<a href="{res["link"]}" class="news-link">{f_title}</a>{SRC_BADGE}</div>'
                    ticker_news_count += 1
                    used_links_ticker.add(res["link"])

        # V30.4.9: Aggressive Content-Backfill (The 15-Article Quota)
        # If specific ticker news is sparse, we pull deeper from the tracker and then the pool.
        if ticker_news_count < 15:
            for t in self.watchlist:
                for i in range(2, 10):  # Check up to 10 articles per ticker
                    if ticker_news_count >= 15:
                        break
                    if len(ticker_tracker[t]) > i:
                        res = ticker_tracker[t][i]
                        if res["link"] not in used_links_ticker:
                            row_bg = "#0f172a" if ticker_news_count % 2 == 0 else "#020617"
                            cleaned_title = (
                                re.sub(r"\s+[-|•|–]\s+.*$", "", res.get("title", ""))
                                .strip()
                                .replace("📊", "»")
                            )
                            f_title = self.inject_price_flair(cleaned_title, prices)
                            src_label = res.get("display_source", res.get("source", ""))[:22]
                            pub_date = format_news_date(res.get("date") or res.get("timestamp"))
                            DATE_STR = (
                                f'<span style="font-size:10px; color:{self.COLOR_DIM}; margin-left:8px;">{pub_date}</span>'
                                if pub_date
                                else ""
                            )
                            SRC_BADGE = (
                                f'&nbsp;<span class="src-badge">[{src_label}]</span>{DATE_STR}'
                            )
                            ticker_news_rows += f'<div style="background-color:{row_bg}; padding:10px 14px; margin-bottom:6px; border-radius:4px; border-left:3px solid {accent}; color:{text_bright};"><span style="font-size:14px; color:{accent};">◈</span>&nbsp;<a href="{res["link"]}" class="news-link">{f_title}</a>{SRC_BADGE}</div>'
                            ticker_news_count += 1
                            used_links_ticker.add(res["link"])

        # Final Fallback: If still under 15, pull directly from ticker_news_pool (all surgical hits)
        if ticker_news_count < 15:
            for res in ticker_news_pool:
                if ticker_news_count >= 15:
                    break
                if res["link"] not in used_links_ticker:
                    row_bg = "#0f172a" if ticker_news_count % 2 == 0 else "#020617"
                    cleaned_title = (
                        re.sub(r"\s+[-|•|–]\s+.*$", "", res.get("title", ""))
                        .strip()
                        .replace("📊", "»")
                    )
                    f_title = self.inject_price_flair(cleaned_title, prices)
                    src_label = res.get("display_source", res.get("source", ""))[:22]
                    pub_date = format_news_date(res.get("date") or res.get("timestamp"))
                    DATE_STR = (
                        f'<span style="font-size:10px; color:{self.COLOR_DIM}; margin-left:8px;">{pub_date}</span>'
                        if pub_date
                        else ""
                    )
                    SRC_BADGE = f'&nbsp;<span class="src-badge">[{src_label}]</span>{DATE_STR}'
                    ticker_news_rows += f'<div style="background-color:{row_bg}; padding:10px 14px; margin-bottom:6px; border-radius:4px; border-left:3px solid {accent}; color:{text_bright};"><span style="font-size:14px; color:{accent};">◈</span>&nbsp;<a href="{res["link"]}" class="news-link">{f_title}</a>{SRC_BADGE}</div>'
                    ticker_news_count += 1
                    used_links_ticker.add(res["link"])

        for res in headlines:
            if res["link"] in used_links_ticker:
                continue
            raw_title = res.get("title", "").upper()
            raw_title_clean = res.get("title", "")
            cleaned_title = (
                re.sub(r"\s+[-|•|–]\s+.*$", "", raw_title_clean).strip().replace("📊", "»")
            )
            f_title = self.inject_price_flair(cleaned_title, prices)
            feed_name = res.get("source", "")
            src_label = res.get("display_source", feed_name)[:22]
            src_label = re.sub(
                r"\.(COM|NET|ORG|CO|UK|IO|AI|INFO|EDU|GOV|US|BIZ|ME)$",
                "",
                src_label,
                flags=re.IGNORECASE,
            )
            pub_date = format_news_date(res.get("date") or res.get("timestamp"))
            DATE_STR = (
                f'<span style="font-size:10px; color:{self.COLOR_DIM}; margin-left:8px;">{pub_date}</span>'
                if pub_date
                else ""
            )
            SRC_BADGE = f'&nbsp;<span class="src-badge">[{src_label}]</span>{DATE_STR}'
            is_earn = (
                res.get("is_earnings") or "EARNINGS" in raw_title or feed_name == "CNBC Earnings"
            )
            # V30.4.9: Authoritative News Integrity check (Semi vs Macro)
            is_semi = is_semi_article(res)

            if is_semi:
                if semi_count < 15:
                    row_bg = "#1e1b4b" if semi_count % 2 == 0 else "#0f172a"
                    semi_trade_rows += f'<div style="background-color:{row_bg}; padding:10px 14px; margin-bottom:6px; border-radius:4px; border-left:3px solid {gold};"><span style="font-size:14px; color:{gold};">★</span>&nbsp;<a href="{res["link"]}" class="news-link">{f_title}</a>{SRC_BADGE}</div>'
                    semi_count += 1
                # STRICT EXCLUSIVITY: No fall-through for technical news
            elif is_earn and earn_count < 10:
                row_bg = "#082f49" if earn_count % 2 == 0 else "#0f172a"
                earnings_intel_rows += f'<div style="background-color:{row_bg}; padding:6px 8px; margin-bottom:4px; border-radius:6px; border:1px solid #1e293b; color:#64748b; font-weight:600;"><span style="font-size:14px; color:#38bdf8;">◈</span>&nbsp;<a href="{res["link"]}" class="news-link">{f_title}</a>{SRC_BADGE}</div>'
                earn_count += 1
            elif row_count < 25:
                # This is the Macro section. It MUST NOT contain is_semi news.
                row_bg = "#1e293b" if row_count % 2 == 0 else "#0f172a"
                row_border = "#334155" if row_count % 2 == 0 else accent
                macro_intel_rows += f'<div style="background-color:{row_bg}; padding:10px 14px; margin-bottom:6px; border-radius:4px; border-left:3px solid {row_border}; color:{text_bright};"><span style="font-size:14px;">&bull;</span>&nbsp;<a href="{res["link"]}" class="news-link">{f_title}</a>{SRC_BADGE}</div>'
                row_count += 1

        syn_html = ""
        if synopsis_data:
            for item in synopsis_data:
                content = item.get("text", "")
                if content:
                    syn_html += f'<div style="margin-bottom:20px; border-left:4px solid {accent}; padding-left:15px; background:rgba(56,189,248,0.02); padding-top:10px; padding-bottom:10px; border-radius:0 4px 4px 0;"><div style="font-family:monospace !important; font-size:11px; color:{accent}; letter-spacing:1px; margin-bottom:8px; text-transform:uppercase; font-weight:900;">[ {item.get("source")} ANALYSIS ]</div><div style="font-size:14px; color:{text_bright}; line-height:1.6; font-family:monospace !important;">{content}</div></div>'

        def render_bucket(title, items, columns=1):
            if not items:
                return ""
            rows = []
            for t in items:
                sym = get_display_symbol(t.get("symbol", ""))
                p_entry = prices.get(t["symbol"], {})
                price, pct, sess = self.get_session_data(p_entry, t["symbol"])
                has_price = price and price > 0
                clr = text_dim
                close_line = ""
                session_key = ""
                if has_price:
                    clr = bull if pct >= 0 else bear
                    label_text, label_color = self._get_session_badge(sess)
                    session_key = (
                        f'<span style="color:{label_color}; font-weight:900;">{label_text}</span>'
                    )
                    if sess in ["PRE", "AH", "OVN", "POST"]:
                        c_p = p_entry.get("close_price") or p_entry.get("price")
                        c_pct = p_entry.get("change_pct", 0)
                        if c_p:
                            c_clr = bull if c_pct >= 0 else bear
                            close_line = f'<div class="tk-c">C: ${c_p:,.2f} <span style="color:{c_clr}">{c_pct:+.2f}%</span></div>'
                price_str = f'<span class="tk-prc">${t["price"]:,.2f}</span>'
                pct_display = f'{price_str}<span class="tk-pct" style="color:{clr};">{session_key} {t["pct"]:+.2f}%</span>'
                val_row = self._render_valuation_row(t)
                rows.append(f"""<div class="tk-row" style="border-left:3px solid {clr};">
                    <table class="tk-table"><tr>
                        <td class="tk-sym"><a href="https://finance.yahoo.com/quote/{t['symbol']}" style="color:#f59e0b; text-decoration:none;">${sym}</a></td>
                        <td class="tk-rt">{pct_display}</td>
                    </tr></table>
                    {close_line}
                    {val_row}
                </div>""")
            if columns == 2:
                half = (len(rows) + 1) // 2
                col1 = "".join(rows[:half])
                col2 = "".join(rows[half:])
                content = f'<table width="100%" cellpadding="0" cellspacing="0"><tr><td class="bucket-col" width="50%" style="vertical-align:top; padding-right:4px;">{col1}</td><td class="bucket-col" width="50%" style="vertical-align:top; padding-left:4px;">{col2}</td></tr></table>'
            else:
                content = "".join(rows)
            return f'<div style="margin-top:10px;"><div class="section-hdr">{title}</div>{content}</div>'

        watchlist_html = render_bucket("REAL-TIME WATCHLIST", watchlist_data, columns=2)
        html = f"""<!DOCTYPE html><html lang="en" style="background-color:#020617; margin:0; padding:0;"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin:0; padding:0; background-color:#020617; font-family:sans-serif; }}
        table {{ border-collapse:collapse; border-spacing:0; border:0; }}
        .wrap {{ background:#0f172a; background:linear-gradient(180deg, #0f172a 0%, #020617 100%); padding:20px 16px; }}
        .main-table {{ width:100%; margin:0 auto; }}
        .section-hdr {{ font-size:20px; font-family:monospace; color:#f59e0b; letter-spacing:4px; text-transform:uppercase; font-weight:900; margin-top:25px; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(245,158,11,0.3); text-shadow: 0 2px 4px rgba(0,0,0,0.5); text-align:center; }}
        .news-link {{ text-decoration:none !important; font-size:14px; font-weight:600; color:#f8fafc !important; font-family:monospace !important; }}
        .src-badge {{ color:#f97316; font-size:10px; font-weight:900; letter-spacing:0.5px; text-transform:uppercase; vertical-align:middle; opacity:0.8; font-family:monospace !important; }}
        .nav-bar {{ position: sticky; top: 0; z-index: 1000; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(56, 189, 248, 0.2); display: flex; justify-content: center; gap: 10px; padding: 10px; }}
        .nav-btn {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #38bdf8; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; font-family:monospace !important; }}
        .home-btn {{ position: fixed; bottom: 30px; right: 30px; width: 50px; height: 50px; background: #000000; color: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; font-weight: 900; box-shadow: 0 4px 15px rgba(0,0,0,0.6); z-index: 1000; font-size: 24px; border: 1px solid rgba(255,255,255,0.2); transition: all 0.2s ease; }}
        .home-btn:hover {{ background: #111111; transform: scale(1.1); border-color: #38bdf8; }}
        .tk-row {{ background:#1e293b; padding:5px 12px; border-radius:4px; margin-bottom:4px; }}
        .tk-table {{ border-collapse:collapse; width:100%; }}
        .tk-sym {{ font-weight:bold; font-size:18px; }}
        .tk-rt {{ text-align:right; }}
        .tk-prc {{ color:#cbd5e1; font-size:13px; margin-right:6px; }}
        .tk-pct {{ font-weight:bold; font-size:14px; }}
        .tk-c {{ font-size:10px; color:#64748b; font-weight:normal; margin-top:2px; }}
        .tk-notes {{ font-size:12px; color:#8f9bb3; margin-top:6px; line-height:1.6; overflow:hidden; max-height:80px; }}
        .tk-val {{ text-align:left; font-size:10px; color:#38bdf8; font-family:monospace; margin-top:2px; }}
        @media only screen and (max-width:768px) {{
            .bucket-col {{ display:block !important; width:100% !important; padding:0 !important; }}
            .home-btn {{ width: 50px !important; height: 50px !important; font-size: 28px !important; bottom: 20px !important; right: 20px !important; border-color: rgba(56, 189, 248, 0.8) !important; }}
        }}
    </style></head><body id="top" style="background-color:#020617; margin:0; padding:0;">
    <div class="nav-bar"><a href="#synopsis" class="nav-btn">Synopsis</a><a href="#macro" class="nav-btn">Macro</a><a href="#ticker-news" class="nav-btn">Tickers</a><a href="#earn" class="nav-btn">Earnings</a><a href="#semi" class="nav-btn">Semi</a><a href="#ticker" class="nav-btn">Watchlist</a></div><a href="#top" class="home-btn">&uarr;</a>
    <div style="background-color:#020617; margin:0; padding:0; font-family:monospace, sans-serif;"><table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#020617" style="background-color:#020617; margin:0; padding:0;"><tr><td align="center" bgcolor="#020617" style="padding:20px 16px; background-color:#020617;">
    <table class="main-table" width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#0f172a" style="max-width:800px; width:100%; text-align:left; font-family:monospace, sans-serif; background-color:#0f172a; border-radius:8px; overflow:hidden; border:1px solid #1e293b;">
    <tr><td class="header-cell" style="padding:25px; border-bottom: 2px solid #6366f1;" bgcolor="#0f172a">
        <div class="hdr-title" style="font-size:24px; font-weight:900; color:#f8fafc; text-align:center; letter-spacing:1px; font-family:monospace !important; text-transform:uppercase;">NEWS <span style="color:#6366f1;">INTELLIGENCE</span></div>
        <div class="hdr-sub" style="font-size:10px; color:#64748b; text-align:center; margin-top:5px; font-family:monospace !important; text-transform:uppercase;">{VERSION} // {get_header_timestamp(self.now)} EST // <a href="https://bmwseals.com/stocks/news" style="color:#38bdf8; text-decoration:none; font-weight:bold;">PORTAL ACCESS</a></div>
    </td></tr>
    <tr><td class="wrap" bgcolor="#0f172a">
        <div id="synopsis" class="section-hdr">MARKET ANALYSIS OVERVIEW</div>{syn_html}
        <div id="macro" class="section-hdr">MACRO INTELLIGENCE</div>{macro_intel_rows}
        <div id="ticker-news" class="section-hdr">TICKER-SPECIFIC INTEL</div>{ticker_news_rows}
        <div id="earn" class="section-hdr">EARNINGS INTELLIGENCE</div>{earnings_intel_rows}
        <div id="semi" class="section-hdr">SEMI INSIGHT</div>{semi_trade_rows}
        <div id="ticker">{watchlist_html}</div>
        <div style="text-align:center; color:#64748b; font-size:10px; font-family:monospace; padding:40px 0;">END OF DOSSIER // TRANSMISSION SECURE // SOVEREIGN NEWS ENGINE {VERSION}</div>
    </td></tr></table></td></tr></table></div></body></html>"""
        return re.sub(r">\s+<", "><", html).strip()

    def send_email(self, html, subject_override=None):
        u = os.getenv("GMAIL_USER")
        pk = os.getenv("GMAIL_APP_PASS")
        r = os.getenv("RECIPIENT_EMAIL", "rayjonesy@gmail.com")
        if not u or not pk:
            print("[ERR] Email credentials missing (GMAIL_USER/GMAIL_APP_PASS)")
            return False
        display_name = os.getenv("GMAIL_DISPLAY_NAME", "Market News")
        salt = uuid.uuid4().hex[:8]
        msg = MIMEMultipart()
        msg["From"] = f"{display_name} <{u}>"
        msg["To"] = r
        msg["Subject"] = (
            subject_override
            if subject_override
            else f"Sovereign News Intelligence // {self.now.strftime('%m/%d/%y')} [{salt}]"
        )
        # V28 Hardening: Anti-clip protection
        html_anti_clip = html.replace(
            "</body>",
            f'<div style="display:none; color:transparent; font-size:0px; height:0px;">Anti-clip UUID: {uuid.uuid4().hex} - Time: {datetime.datetime.now().isoformat()}</div></body>',
        )
        msg.attach(MIMEText(html_anti_clip, "html"))
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(u, pk)
                server.send_message(msg)
            print("[OK] NEWS EMAIL DISPATCHED.")
            return True
        except Exception as e:
            print(f"[ERR] Email failed: {e}")
            return False

    async def run(self, send_mail=False):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting Mirror Engine...")
        data = await self.gather_all_data()
        html = await self.compose_html(data)
        preview_path = self.db_path / "news_preview.html"
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html)
        if hasattr(RemoteSync, "sync_file"):
            RemoteSync.sync_file(preview_path)
        if send_mail:
            self.send_email(html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", action="store_true")
    parser.add_argument("--tickers", type=str, help="Path to tickers.txt")
    args = parser.parse_args()
    engine = NewsMarketSynopsisEngine()
    if args.tickers:
        engine.watchlist = engine._load_watchlist(args.tickers)
    asyncio.run(engine.run(send_mail=args.email))


if __name__ == "__main__":
    main()
