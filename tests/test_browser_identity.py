import re
from pathlib import Path

import pytest

from engine.paywall_intelligence import PaywallIntelligence
from engine.stealth_navigator import USER_AGENTS


def test_navigator_ua_consistency():
    """Verify StealthNavigator uses Chrome 146."""
    for ua in USER_AGENTS:
        assert "Chrome/146" in ua


def test_paywall_ua_consistency():
    """Verify PaywallIntelligence uses Chrome 146."""
    assert "Chrome/146" in PaywallIntelligence.CHROME_146


def test_file_references_sync():
    """Grep check for any remaining '160.0.8827' strings in engine/."""
    engine_path = Path("engine")
    mismatches = []
    for p in engine_path.glob("*.py"):
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback for any legacy files
            content = p.read_text(encoding="latin-1")
        if "160.0.8827" in content:
            mismatches.append(str(p))

    assert not mismatches, f"Stale Chrome 160 references found in: {mismatches}"


if __name__ == "__main__":
    pytest.main([__file__])
