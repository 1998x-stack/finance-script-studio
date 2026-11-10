"""Guard the distinction between structurally valid scripts and approved releases."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from qa_finance100 import evaluate, suggested_times


class Finance100ProductionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = evaluate(ROOT)

    def test_full_coverage_and_draft_only(self):
        self.assertEqual(self.report["summary"]["episodes"], 100)
        self.assertEqual(len(self.report["episodes"]), 100)
        self.assertTrue(all(e["publication_gate"] == "blocked"
                            for e in self.report["episodes"]))
        self.assertEqual(self.report["summary"]["human_signoff_complete"], 0)
        self.assertEqual(self.report["summary"]["published_authorized"], 0)

    def test_all_have_structural_integrity(self):
        # This test intentionally fails if script, JSON or storyboard drift.
        errors = {e["episode"]: e["errors"] for e in self.report["episodes"] if e["errors"]}
        self.assertEqual(errors, {}, errors)

    def test_performance_warnings_do_not_grant_approval(self):
        self.assertGreater(self.report["summary"]["pacing_warnings"], 0)
        self.assertTrue(any("pacing_over_250_characters_per_minute" in e["warnings"]
                            for e in self.report["episodes"]))
        for ep in self.report["episodes"]:
            self.assertEqual(sum(ep["proposed_trial_seconds"]), 180)
            self.assertEqual(len(ep["proposed_trial_seconds"]), 5)
            self.assertTrue(all(s > 0 for s in ep["proposed_trial_seconds"]))

    def test_proportional_trial_times_not_claimed_as_recorded(self):
        self.assertEqual(sum(suggested_times([50, 70, 300, 90, 50])), 180)
        self.assertNotEqual(suggested_times([50, 70, 300, 90, 50]),
                            [15, 30, 60, 45, 30])


if __name__ == "__main__":
    unittest.main()
