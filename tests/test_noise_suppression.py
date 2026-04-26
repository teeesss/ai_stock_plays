import asyncio
import sys
from pathlib import Path

# Add engine to path
sys.path.append(str(Path.cwd() / "engine"))

from local_nlp import LocalIntelligenceSynthesizer
from macro_aggregator import MacroAggregator
from stress_test_data import SYNTHETIC_HEADLINES


async def run_stress_test():
    agg = MacroAggregator()
    nlp = LocalIntelligenceSynthesizer()

    print(f"[TEST START] Testing {len(SYNTHETIC_HEADLINES)} Synthetic Headlines...\n")

    results = {
        "ALPHA_PASSED": 0,
        "ALPHA_FAILED": 0,
        "NOISE_PASSED": 0,  # LEAKS!
        "NOISE_FAILED": 0,
    }

    leaks = []
    false_positives = []

    # We will simulate the aggregator building the raw items
    simulated_items = []

    for item in SYNTHETIC_HEADLINES:
        # 1. Aggregator Phase (Check Blacklist & Score)
        # Note: we bypass the actual network fetch but use the logic
        title = item["title"]
        source = item["source"]
        expected = item["expected"]
        t = item["type"]

        # Check Blacklist directly
        is_safe = agg.is_article_safe(
            title, f"http://test.com/{hash(title)}", source, feed_name=source
        )

        if not is_safe:
            # Blacklisted! It fails immediately.
            final_score = -999.0
            if expected == "FAIL":
                results["NOISE_FAILED"] += 1
            else:
                results["ALPHA_FAILED"] += 1
                false_positives.append((title, final_score, source, "Blacklisted"))
            continue

        # Aggregator base score
        content_score, base_weight = agg.score_headline(title, source)

        # Add to NLP input
        simulated_items.append(
            {
                "title": title,
                "raw_title": title,
                "link": f"http://test.com/{hash(title)}",
                "source": source,
                "display_source": source,
                "base_weight": base_weight,
                "content_score": content_score,
                "score": base_weight + content_score,
                "expected": expected,
                "type": t,
            }
        )

    # 2. NLP Phase
    # Rank them
    semi_sources = ["ZH Tech", "ZH Markets"]  # Standard semi sources
    ranked = nlp.rank_news_relevance(simulated_items, top_n=500, specialized_sources=semi_sources)

    # We need to evaluate the ones that survived ranking
    # The ranker filters out anything < relevance_floor (unless specialized)
    survived_links = {r["link"]: r["final_score"] for r in ranked}

    for item in simulated_items:
        title = item["title"]
        expected = item["expected"]
        source = item["source"]
        t = item["type"]
        link = item["link"]

        passed_floor = link in survived_links
        final_score = survived_links.get(link, item["score"])  # approximate if failed

        # Check if specialized bypass triggered incorrectly
        if passed_floor:
            if expected == "PASS":
                results["ALPHA_PASSED"] += 1
            else:
                results["NOISE_PASSED"] += 1
                leaks.append((title, final_score, source, t))
        else:
            if expected == "FAIL":
                results["NOISE_FAILED"] += 1
            else:
                results["ALPHA_FAILED"] += 1
                false_positives.append((title, final_score, source, t))

    print("=" * 60)
    print(" STRESS TEST RESULTS")
    print("=" * 60)
    print(f" Total Headlines: {len(simulated_items)}")
    print(f" Alpha Passed (Good):  {results['ALPHA_PASSED']}")
    print(f" Alpha Failed (Bad):   {results['ALPHA_FAILED']}")
    print(f" Noise Failed (Good):  {results['NOISE_FAILED']}")
    print(f" Noise Passed (LEAK!): {results['NOISE_PASSED']}")
    print("=" * 60)

    if leaks:
        print("\n[LEAKS DETECTED] The following noise passed the 28.0 floor (Showing first 10):")
        for title, score, src, t in leaks[:10]:
            print(f"  - [{src}] Score: {score:.1f} | Type: {t} | {title}")

    if false_positives:
        print("\n[FALSE POSITIVES] The following alpha fell below the floor (Showing first 10):")
        for title, score, src, t in false_positives[:10]:
            print(f"  - [{src}] Score: {score:.1f} | Type: {t} | {title}")

    if not leaks and not false_positives:
        print("\n[SUCCESS] Engine correctly filtered 100% of headlines.")


if __name__ == "__main__":
    asyncio.run(run_stress_test())
