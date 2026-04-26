import json
import os
import sys
import time
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestSyncDeduplication(unittest.TestCase):
    def setUp(self):
        self.test_db = "database/TEST_NEWS_DB.json"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_deduplication_logic(self):
        """Simulate merging duplicate articles into the DB."""
        # Initial State: 1 article
        initial_data = {
            "title": "Stock Up 10%",
            "link": "http://yahoo.com/1",
            "provider": "Yahoo",
            "date": int(time.time()),
            "vibe_score": 0.5,
        }

        # 1. Save Initial
        with open(self.test_db, "w") as f:
            json.dump({"news": {"AAPL": [initial_data]}}, f)

        # 2. Simulate bridge merge logic
        current_db = {"news": {"AAPL": [initial_data]}}
        fresh_fetch = [
            initial_data,  # DUPE
            {
                "title": "New News",
                "link": "http://yahoo.com/2",
                "provider": "Yahoo",
                "date": int(time.time()) + 10,
                "vibe_score": 0.1,
            },
        ]

        # Merge logic implementation (to be tested)
        existing_titles = {a["title"] for a in current_db["news"]["AAPL"]}
        new_entries = [a for a in fresh_fetch if a["title"] not in existing_titles]
        current_db["news"]["AAPL"] = new_entries + current_db["news"]["AAPL"]

        # 3. Assert
        self.assertEqual(
            len(current_db["news"]["AAPL"]),
            2,
            "Should have 2 articles (1 new, 1 dupe filtered)",
        )
        self.assertEqual(
            current_db["news"]["AAPL"][0]["title"],
            "New News",
            "Newest should be at the top",
        )

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)


if __name__ == "__main__":
    unittest.main()
