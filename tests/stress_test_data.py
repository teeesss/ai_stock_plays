import random

# Base components for generating diverse headlines
ALPHA_SUBJECTS = [
    "Nvidia",
    "TSMC",
    "Anthropic",
    "Meta",
    "Goldman Sachs",
    "Morgan Stanley",
    "Hedge Funds",
    "Prime Brokerage",
]
ALPHA_ACTIONS = [
    "Secures $10B Order",
    "Announces Breakthrough",
    "Upgrades Guidance",
    "Pivots Strategy",
    "Resolves Bottleneck",
    "Forecasts Record Surge",
]
ALPHA_CONTEXTS = [
    "in Silicon Photonics",
    "for Next-Gen GPU Cluster",
    "Amid Undervalued Earnings",
    "for AI Bets",
    "in Semiconductor Contracts",
]

MACRO_SUBJECTS = [
    "Fed Chairman",
    "US GDP",
    "China's Economy",
    "Global Oil Demand",
    "Middle East Tensions",
    "Inflation",
]
MACRO_ACTIONS = [
    "Announces Unexpected Pivot",
    "Hits Record High",
    "Falters Unexpectedly",
    "Accelerates Growth",
    "Triggers Contagion Fears",
]
MACRO_CONTEXTS = [
    "Defying Forecasts",
    "Amid Rate Hikes",
    "in Strait of Hormuz",
    "in Real Estate Defaults",
    "Across Global Markets",
]

NOISE_SUBJECTS = [
    "Warren Buffett",
    "Jim Cramer",
    "Dave Ramsey",
    "American Teens",
    "Teenagers",
    "Roblox",
    "Kardashian",
    "Nancy Pelosi",
    "Netanyahu",
    "Cash App",
]
NOISE_ACTIONS = [
    "Says This ETF is a Better Trade",
    "Endorses New Trend",
    "Settles Lawsuit Over Children",
    "Diagnosed With Rare Illness",
    "Announces Record Quarter",
    "Dumping Crypto",
]
NOISE_CONTEXTS = [
    "for Your Kids",
    "in Most Surveilled Cities",
    "Amid Lifestyle Brand Expansion",
    "for Summer Vacation",
    "in the New Era of Entertainment",
]

LEGAL_SUBJECTS = ["Securities Litigation", "Class Action", "Investor Counsel", "Lawsuit Filed"]
LEGAL_ACTIONS = [
    "Reaches Deadline",
    "Targets Major Tech Firm",
    "Allegedly Using Stolen Tech",
    "Settles With 3 States",
]
LEGAL_CONTEXTS = [
    "Over Securities Fraud",
    "in Legal Battle",
    "Over Endangering Children",
    "in New Court Ruling",
]

SOURCES = [
    "ZH Tech",
    "ZH Markets",
    "ZH Economics",
    "ZH Energy",
    "WSJ Markets",
    "OilPrice",
    "Business Insider",
    "MotleyFool",
    "CNBC",
]


def generate_dataset(num_items=200):
    dataset = []

    # Ensure we get a balanced mix
    types = ["ALPHA", "MACRO", "SNEAKY_NOISE", "PURE_FLUFF", "LEGAL", "RANDOM_JUNK"]

    for i in range(num_items):
        t = random.choice(types)
        source = random.choice(SOURCES)

        if t == "ALPHA":
            title = f"{random.choice(ALPHA_SUBJECTS)} {random.choice(ALPHA_ACTIONS)} {random.choice(ALPHA_CONTEXTS)}"
            expected = "PASS"
        elif t == "MACRO":
            title = f"{random.choice(MACRO_SUBJECTS)} {random.choice(MACRO_ACTIONS)} {random.choice(MACRO_CONTEXTS)}"
            expected = "PASS"
        elif t == "SNEAKY_NOISE":
            # Mix alpha subjects with noise contexts to try to trick the engine
            title = f"{random.choice(ALPHA_SUBJECTS)} {random.choice(NOISE_ACTIONS)} {random.choice(NOISE_CONTEXTS)}"
            expected = "FAIL"
        elif t == "PURE_FLUFF":
            title = f"{random.choice(NOISE_SUBJECTS)} {random.choice(NOISE_ACTIONS)} {random.choice(NOISE_CONTEXTS)}"
            expected = "FAIL"
        elif t == "LEGAL":
            title = f"{random.choice(LEGAL_SUBJECTS)} {random.choice(LEGAL_ACTIONS)} {random.choice(LEGAL_CONTEXTS)}"
            expected = "FAIL"
        else:
            # Complete random nonsense
            words = [
                "Weight Gain",
                "Trees",
                "Chestnuts",
                "Malaria",
                "Drones",
                "Baseball",
                "Football",
                "K-Pop",
                "Celebrity",
                "Diet",
                "Xbox",
                "Subscription",
            ]
            title = " ".join(random.sample(words, 5))
            expected = "FAIL"

        dataset.append({"title": title, "source": source, "expected": expected, "type": t})

    return dataset


# For external importing
SYNTHETIC_HEADLINES = generate_dataset(200)

if __name__ == "__main__":
    print(f"Generated {len(SYNTHETIC_HEADLINES)} headlines.")
    print("Sample:")
    for h in SYNTHETIC_HEADLINES[:5]:
        print(f" - [{h['expected']}] ({h['type']}) {h['title']}")
