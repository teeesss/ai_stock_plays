import pytest
from bs4 import BeautifulSoup
from engine.scraper.dom_parser import parse_tweet, garbage_purge

def test_garbage_purge():
    assert garbage_purge("") is True
    assert garbage_purge("short") is True
    assert garbage_purge("This is a valid tweet about $NVDA and HBM4.") is False
    assert garbage_purge("Airdrop Solana Free Money") is True

def test_parse_tweet_basic():
    html = """
    <div class="timeline-item">
        <div class="tweet-content">Testing $ N V D A and $ A A O I fragments.</div>
        <div class="tweet-date"><a href="/user/status/12345" title="Apr 13, 2026">date</a></div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    item = soup.select_one(".timeline-item")
    result = parse_tweet(item, "testuser")
    
    assert result is not None
    assert result["id"] == "12345"
    assert "$NVDA" in result["text"] or "$ NVDA" in result["text"] # Check current logic
    assert "testuser" in result["url"]

def test_parse_tweet_cashtags():
    html = """
    <div class="timeline-item">
        <div class="tweet-content">
            Check <a class="cashtag">$<span>N</span><span>V</span><span>D</span><span>A</span></a>
        </div>
        <div class="tweet-date"><a href="/u/s/999" title="now">now</a></div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    item = soup.select_one(".timeline-item")
    result = parse_tweet(item, "trader")
    assert "$NVDA" in result["text"]
