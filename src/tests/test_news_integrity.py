"""
src/tests/test_news_integrity.py
================================
Regression test for News Intelligence Categorization (V30.4.9).
Ensures technical semiconductor news is correctly isolated from Macro sections.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).parent.parent.parent
sys.path.append(str(root))

try:
    from engine.ticker_utils import is_semi_article
except ImportError:
    from ticker_utils import is_semi_article


def test_semi_categorization():
    print("[TEST] Starting News Integrity Verification...")

    test_cases = [
        {
            "res": {
                "title": "Athos Scraps Multi-Vendor Roadmap, Plans Chiplet Tape-Out",
                "source": "EE Times Semi",
                "is_semi": True,
            },
            "expected_semi": True,
            "desc": "Technical EE Times article (Flagged is_semi)",
        },
        {
            "res": {
                "title": "Solving the EDA tool fragmentation crisis",
                "source": "SemiWiki",
                "is_semi": False,  # Test keyword fallback
            },
            "expected_semi": True,
            "desc": "Technical SemiWiki article (Keyword fallback: EDA TOOL)",
        },
        {
            "res": {
                "title": "NVIDIA Blackwell Demand Surges in Q1",
                "source": "WSJ",
                "is_semi": False,
            },
            "expected_semi": False,
            "desc": "Macro NVIDIA news from WSJ (Should stay Macro for high-level insight)",
        },
        {
            "res": {
                "title": "Timestamp Drift and Sensor Synchronization: Small Timing Errors",
                "source": "EE Times Semi",
                "is_semi": True,
            },
            "expected_semi": True,
            "desc": "Technical sensor news (Flagged is_semi)",
        },
    ]

    failures = 0
    for i, case in enumerate(test_cases):
        res = case["res"]
        actual = is_semi_article(res)
        if actual == case["expected_semi"]:
            print(f"  [PASS] Case {i+1}: {case['desc']}")
        else:
            print(
                f"  [FAIL] Case {i+1}: {case['desc']} (Expected {case['expected_semi']}, Got {actual})"
            )
            failures += 1

    if failures == 0:
        print("\n[SUCCESS] All news integrity tests passed.")
        sys.exit(0)
    else:
        print(f"\n[FAILURE] {failures} tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    test_semi_categorization()
