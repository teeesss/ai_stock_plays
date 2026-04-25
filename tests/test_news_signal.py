import pytest
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from engine.macro_aggregator import MacroAggregator

@pytest.fixture
def agg():
    return MacroAggregator()

def test_source_spacing(agg):
    # Requirement: YAHOOFINANCE -> YAHOO FINANCE
    assert agg.normalize_source("YAHOOFINANCE") == "YAHOO FINANCE"
    assert agg.normalize_source("OILPRICEMACRO") == "OIL PRICE MACRO"
    assert agg.normalize_source("ECONTIMES") == "ECON TIMES"
    assert agg.normalize_source("SOUTHCHINAMORNINGPO") == "SOUTH CHINA MORNING PO"

def test_blacklist_buffett(agg):
    # Requirement: Blacklist Warren Buffett
    assert agg.is_article_safe("According to Warren Buffett's math", "link", "FORTUNE") == False
    assert agg.is_article_safe("Buffet says buy", "link", "CNBC") == False

def test_title_length_gate(agg):
    # Requirement: Reject titles under 4 words
    assert agg.is_article_safe("Macroscope", "link", "SCMP") == False
    assert agg.is_article_safe("Stocks fall again", "link", "BBC") == False # 3 words
    assert agg.is_article_safe("Nvidia smashes all records", "link", "TECH") == True # 4 words

def test_opinion_and_junk_gate(agg):
    # Requirement: Reject opinion columns/clickbait questions
    assert agg.is_article_safe("Why should I care if share prices fall?", "link", "BBC") == False
    assert agg.is_article_safe("Can you beat the market?", "link", "TRIBUNE") == False
    assert agg.is_article_safe("How to save for retirement", "link", "TRIBUNE") == False
    
    # Declarative institutional news should pass
    assert agg.is_article_safe("Nvidia Blackwell production ramps up as demand surges", "link", "REUTERS") == True
