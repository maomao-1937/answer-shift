import unittest

from answer_shift.core import compare, read_jsonl


class FakeScorer:
    def score_many(self, pairs):
        return [
            {"contradiction": 0.9, "entailment": 0.02, "neutral": 0.08}
            if "EU-West" in a + b and "US-East" in a + b
            else {"contradiction": 0.01, "entailment": 0.98, "neutral": 0.01}
            for a, b in pairs
        ]


class CoreTests(unittest.TestCase):
    def test_jsonl_rejects_duplicate_id(self):
        with self.assertRaises(ValueError):
            read_jsonl('{"case_id":"x","answer":"first"}\n{"case_id":"x","answer":"second"}')

    def test_reports_changes_and_added_removed_cases(self):
        result = compare(
            {"x": "The region is EU-West.", "old": "An old answer."},
            {"x": "The region is US-East.", "new": "A new answer."},
            FakeScorer(),
        )
        self.assertEqual(result["changes"][0]["verdict"], "possible_meaning_change")
        self.assertEqual(result["removed_case_ids"], ["old"])
        self.assertEqual(result["added_case_ids"], ["new"])

    def test_exact_match(self):
        result = compare({"a": "Same answer."}, {"a": "Same answer."}, FakeScorer())
        self.assertEqual(result["changes"][0]["verdict"], "exact_match")


if __name__ == "__main__":
    unittest.main()
