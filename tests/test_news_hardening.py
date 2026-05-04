import time

import pytest

from engine.macro_aggregator import MacroAggregator

# V26.10: News Hardening Test Suite
# Tests filtering, freshness, and domain-shield logic.


@pytest.fixture
def agg():
    return MacroAggregator()


def test_rejects_blacklisted_domains(agg):
    # Setup forbidden links
    bad_links = [
        "https://www.aol.com/news/article-123",
        "https://msn.com/en-us/money/stocks",
        "https://www.fool.com/investing/2026/04/25/nvidia-stock-buy-now",
        "https://www.motleyfool.com/article",
    ]
    for link in bad_links:
        # We simulate the filter logic that should return False for bad links
        assert agg.is_article_safe(title="Safe Title", link=link, source="Safe Source") is False


def test_rejects_blacklisted_personalities(agg):
    # Setup forbidden titles
    bad_titles = [
        "Nancy Pelosi's latest stock trade",
        "Jim Cramer says buy Nvidia",
        "Dave Ramsey's advice on debt",
    ]
    for title in bad_titles:
        assert (
            agg.is_article_safe(title=title, link="https://reuters.com/news", source="Reuters")
            is False
        )


def test_enforces_36h_hard_cutoff(agg):
    now = time.time()
    # On weekends, the limit is 60h, otherwise 36h.
    # V29.7: Sunday/Monday Lenience (72h limit)
    is_stasis = agg.market_session.is_market_stasis()
    limit_hours = 60 if is_stasis else 36

    now_est = agg.market_session.get_est_now()
    if now_est.weekday() in [0, 6]:
        limit_hours = 72

    # Just over the limit
    old_ts = now - ((limit_hours + 1) * 3600)
    assert agg.is_fresh_enough(old_ts) is False

    # Just under the limit
    fresh_ts = now - ((limit_hours - 1) * 3600)
    assert agg.is_fresh_enough(fresh_ts) is True


def test_applies_24h_decay(agg):
    now = time.time()
    is_stasis = agg.market_session.is_market_stasis()
    decay_limit = 48 if is_stasis else 24

    # Just over the decay limit (should trigger 50% penalty)
    stale_ts = now - ((decay_limit + 1) * 3600)
    base_score = 100
    decayed_score = agg.apply_freshness_decay(base_score, stale_ts)
    assert decayed_score == 50

    # Just under the decay limit (should have NO penalty)
    fresh_ts = now - ((decay_limit - 1) * 3600)
    assert agg.apply_freshness_decay(base_score, fresh_ts) == 100


def test_rejects_non_english_content(agg):
    bad_titles = [
        "市場の急騰：半導体株",  # Japanese
        "Акції Nvidia зростають",  # Ukrainian
        "Les actions s'envolent",  # French (non-English gate)
    ]
    for title in bad_titles:
        assert (
            agg.is_article_safe(title=title, link="https://globalnews.com", source="Global")
            is False
        )


def test_rejects_paywall_domains(agg):
    # V26.11 Requirement
    paid_links = [
        "https://www.bloomberg.com/news/articles/2026-04-25/stocks-rise",
        "https://www.wsj.com/articles/fed-rates-12345",
        "https://seekingalpha.com/news/408123-nvidia-buy",
        "https://www.barrons.com/articles/stock-market-today-123",
    ]
    for link in paid_links:
        assert agg.is_article_safe(title="Macro News", link=link, source="Institutional") is False


def test_rejects_video_links(agg):
    # V26.11 Requirement
    video_links = [
        "https://www.cnbc.com/video/2026/04/25/nvidia-ceo-interview.html",
        "https://reuters.com/news/video/market-recap",
        "https://finance.yahoo.com/m/video/123456",
    ]
    for link in video_links:
        assert agg.is_article_safe(title="Watch this video", link=link, source="CNBC") is False


def test_enforces_geographic_relevance(agg):
    # V26.11 Requirement: Block niche local news without tech anchors
    assert (
        agg.is_article_safe(
            title="India's RBL Bank profit jumps",
            link="https://reuters.com/india-bank",
            source="Reuters",
        )
        is False
    )

    # Preserve international news if it has a high-alpha tech anchor
    assert (
        agg.is_article_safe(
            title="Taiwan Semiconductor (TSMC) sees AI surge",
            link="https://taiwannews.com/tsmc",
            source="Taiwan News",
        )
        is True
    )
